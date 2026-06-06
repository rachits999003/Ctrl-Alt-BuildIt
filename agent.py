#!/usr/bin/env python3
"""
Ctrl-Alt-BuildIt Agent
Usage:
    python agent.py "create a fullstack react + python task management app"
    python agent.py --provider ollama --model qwen2.5-coder:7b "build a todo app"

Providers supported:
    ollama     (default, local — needs Ollama running)
    anthropic  (needs ANTHROPIC_API_KEY)
    openai     (needs OPENAI_API_KEY)
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

MAX_RETRIES = 3


# ── Provider abstraction ──────────────────────────────────────────

def llm_call(messages: list[dict], provider: str, model: str) -> str:
    """Call the LLM and return the raw text response."""
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model=model or "claude-sonnet-4-6",
            max_tokens=8096,
            messages=messages,
        )
        return resp.content[0].text

    elif provider == "ollama":
        import requests
        base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        r = requests.post(f"{base}/api/chat", json={
            "model": model or "qwen2.5-coder:7b",
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2},
        }, timeout=300)
        r.raise_for_status()
        return r.json()["message"]["content"]

    elif provider == "openai":
        import requests
        key = os.environ.get("OPENAI_API_KEY", "")
        r = requests.post("https://api.openai.com/v1/chat/completions", json={
            "model": model or "gpt-4o",
            "messages": messages,
            "temperature": 0.2,
        }, headers={"Authorization": f"Bearer {key}"}, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    else:
        # Fall back to project's ProviderManager (config/providers.json)
        ROOT = Path(__file__).parent
        sys.path.insert(0, str(ROOT))
        from src.provider_manager.manager import ProviderManager
        pm = ProviderManager.from_config()
        p = pm.get(provider)
        if not p:
            raise ValueError(f"Unknown provider '{provider}'. Configured: {pm.list_providers()}")
        result = p.chat(messages)
        return result["choices"][0]["message"]["content"]


# ── JSON extraction ───────────────────────────────────────────────

def extract_json(raw: str) -> dict:
    """
    Robustly extract a JSON object from raw LLM output.
    Tries in order:
      1. Direct parse of stripped text
      2. Strip markdown fences, then parse
      3. Regex-extract first {...} block, then parse
    Raises ValueError if all attempts fail.
    """
    text = raw.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences (```json ... ``` or ``` ... ```)
    stripped = re.sub(r"```(?:json|python|javascript|typescript|[a-z]*)?\s*", "", text)
    stripped = stripped.replace("```", "").strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 3. Find the outermost {...} block
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # 4. Fix unescaped newlines inside string values (common Qwen artifact)
        fixed = candidate.replace('\n', '\\n').replace('\t', '\\t')
        # but restore structural newlines outside strings by re-extracting
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON object found in response:\n\n{raw[:500]}")


def sanitize_file_content(content: str) -> str:
    """
    Final pass on extracted file content.
    Removes any residual markdown fences that slipped inside the JSON value.
    """
    # Remove leading/trailing fences that sometimes appear inside the value
    content = re.sub(r"^```[a-z]*\n?", "", content)
    content = re.sub(r"\n?```$", "", content)
    return content.strip() + "\n"


# ── Structured LLM calls ──────────────────────────────────────────

PLAN_SYSTEM = """\
You are a senior software architect. Given a project request, output a JSON plan.

RULES:
- Output ONLY a single valid JSON object. No markdown. No fences. No explanation.
- Use this exact schema:
{
  "project_name": "snake_case_name",
  "description": "one sentence",
  "stack": {"frontend": "...", "backend": "...", "database": "..."},
  "files": [
    {"path": "relative/path/file.ext", "description": "what this file does"}
  ]
}
- Include ALL files for a runnable MVP: source files, package.json, requirements.txt, Dockerfile, README.md.
"""

IMPLEMENT_SYSTEM = """\
You are an expert full-stack engineer implementing a single file.

RULES:
- Output ONLY a single valid JSON object. No markdown. No fences. No explanation before or after.
- Use this exact schema:
{"file_content": "complete file contents here"}
- The file_content value must be the raw file text, fully implemented and working.
- Escape special characters properly for JSON strings (newlines as \\n, quotes as \\", etc).
"""

README_SYSTEM = """\
You are a technical writer. Write a concise README.md.

RULES:
- Output ONLY a single valid JSON object. No markdown outside the value. No fences.
- Use this exact schema:
{"file_content": "markdown content here"}
- The file_content value must be complete README markdown with setup and run instructions.
"""


def llm_plan(prompt: str, provider: str, model: str) -> dict:
    """Call LLM for project plan, validate schema, retry on failure."""
    messages = [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": f"Project request: {prompt}"},
    ]
    required_keys = {"project_name", "description", "stack", "files"}

    for attempt in range(1, MAX_RETRIES + 1):
        raw = llm_call(messages, provider, model)
        try:
            plan = extract_json(raw)
            missing = required_keys - plan.keys()
            if missing:
                raise ValueError(f"Plan missing keys: {missing}")
            if not isinstance(plan["files"], list) or not plan["files"]:
                raise ValueError("Plan 'files' must be a non-empty list")
            for f in plan["files"]:
                if "path" not in f or "description" not in f:
                    raise ValueError(f"File entry missing path/description: {f}")
            return plan
        except (ValueError, json.JSONDecodeError) as e:
            print(f"  ⚠ Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                # Feed the error back so the model can self-correct
                messages.append({"role": "assistant", "content": raw})
                messages.append({"role": "user", "content":
                    f"Your response was invalid. Error: {e}\n"
                    "Output ONLY a valid JSON object matching the schema. No other text."
                })

    raise RuntimeError(f"Plan generation failed after {MAX_RETRIES} attempts.")


def llm_file(plan_summary: str, fspec: dict, provider: str, model: str) -> str:
    """Call LLM to implement a single file. Returns sanitized file content."""
    messages = [
        {"role": "system", "content": IMPLEMENT_SYSTEM},
        {"role": "user", "content": (
            f"Project plan:\n{plan_summary}\n\n"
            f"Implement this file: {fspec['path']}\n"
            f"Purpose: {fspec['description']}\n\n"
            "Output ONLY the JSON object with key 'file_content'."
        )},
    ]

    for attempt in range(1, MAX_RETRIES + 1):
        raw = llm_call(messages, provider, model)
        try:
            obj = extract_json(raw)
            if "file_content" not in obj:
                raise ValueError(f"Response missing 'file_content' key. Got keys: {list(obj.keys())}")
            if not isinstance(obj["file_content"], str):
                raise ValueError("'file_content' must be a string")
            return sanitize_file_content(obj["file_content"])
        except (ValueError, json.JSONDecodeError) as e:
            print(f"\n    ⚠ Attempt {attempt}/{MAX_RETRIES} failed: {e}", end="")
            if attempt < MAX_RETRIES:
                messages.append({"role": "assistant", "content": raw})
                messages.append({"role": "user", "content":
                    f"Invalid response. Error: {e}\n"
                    'Output ONLY: {"file_content": "your code here"} — nothing else.'
                })

    raise RuntimeError(f"File generation failed for '{fspec['path']}' after {MAX_RETRIES} attempts.")


# ── Agent steps ───────────────────────────────────────────────────

def step_plan(prompt: str, provider: str, model: str) -> dict:
    print("\n📐 Planning project...")
    plan = llm_plan(prompt, provider, model)
    print(f"  ✓ {plan['project_name']} — {len(plan['files'])} files planned")
    return plan


def step_implement(plan: dict, output_dir: Path, provider: str, model: str):
    print(f"\n🔨 Implementing {len(plan['files'])} files...")
    plan_summary = json.dumps({
        "project_name": plan["project_name"],
        "description": plan["description"],
        "stack": plan["stack"],
        "files": [f["path"] for f in plan["files"]],
    }, indent=2)

    failed = []
    for i, fspec in enumerate(plan["files"], 1):
        fpath = output_dir / fspec["path"]
        fpath.parent.mkdir(parents=True, exist_ok=True)
        print(f"  [{i}/{len(plan['files'])}] {fspec['path']}", end=" ", flush=True)
        try:
            content = llm_file(plan_summary, fspec, provider, model)
            fpath.write_text(content, encoding="utf-8")
            print("✓")
        except RuntimeError as e:
            print(f"\n  ✗ SKIPPED — {e}")
            failed.append(fspec["path"])

    if failed:
        print(f"\n  ⚠ {len(failed)} file(s) skipped: {', '.join(failed)}")


def step_readme(plan: dict, output_dir: Path, provider: str, model: str):
    """Generate README if not already produced by step_implement."""
    readme = output_dir / "README.md"
    if readme.exists() and readme.stat().st_size > 100:
        return
    print("\n📄 Writing README...")
    fspec = {
        "path": "README.md",
        "description": (
            f"Setup and usage instructions for {plan['project_name']}. "
            f"Stack: {json.dumps(plan['stack'])}. "
            f"Include: prerequisites, install steps, how to run, feature list."
        ),
    }
    plan_summary = json.dumps({
        "project_name": plan["project_name"],
        "description": plan["description"],
        "stack": plan["stack"],
        "files": [f["path"] for f in plan["files"]],
    }, indent=2)
    try:
        content = llm_file(plan_summary, fspec, provider, model)
        readme.write_text(content, encoding="utf-8")
        print("  ✓ README.md")
    except RuntimeError as e:
        print(f"  ✗ README skipped — {e}")


# ── CLI entry ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Ctrl-Alt-BuildIt: turn a prompt into a working project"
    )
    parser.add_argument("prompt", help="Project description")
    parser.add_argument("--provider", default="ollama",
                        help="Provider: ollama|anthropic|openai|<config name> (default: ollama)")
    parser.add_argument("--model", default="qwen2.5-coder:7b",
                        help="Model name (default: qwen2.5-coder:7b)")
    parser.add_argument("--output", default="output",
                        help="Output directory (default: ./output)")
    args = parser.parse_args()

    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Ctrl-Alt-BuildIt")
    print(f"   Prompt  : {args.prompt}")
    print(f"   Provider: {args.provider} / {args.model}")
    print(f"   Output  : {output_dir}")

    plan = step_plan(args.prompt, args.provider, args.model)
    (output_dir / "plan.json").write_text(json.dumps(plan, indent=2))

    step_implement(plan, output_dir, args.provider, args.model)
    step_readme(plan, output_dir, args.provider, args.model)

    all_files = [f for f in output_dir.rglob("*") if f.is_file()]
    print(f"\n✅ Done! Project written to: {output_dir}")
    print(f"   Files generated : {len(all_files)}")
    print(f"\nNext steps:")
    print(f"   cat {output_dir}/README.md")


if __name__ == "__main__":
    main()