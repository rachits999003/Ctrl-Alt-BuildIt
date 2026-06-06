# Ctrl Alt BuildIt!

Developer setup

1. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in any provider credentials (e.g., `OPENAI_API_KEY`, `OLLAMA_URL`).

4. Start the provider admin server:

```powershell
python tools\run_server.py
```

5. Run the provider demo:

```powershell
python tools\run_provider_demo.py
```

6. Run tests:

```powershell
pytest -q
```

Notes
- Configure `config/providers.json` to add or change providers.
- Configure `config/routing.json` to map task types to providers.
# Ctrl Alt BuildIt! Prompt Pack

Use these files as the specification for GitHub Copilot, Claude Code, Gemini, or any coding agent.

Recommended build order:
1. vision.md
2. architecture.md
3. prompt-segmentation.md
4. system-prompts.md
5. clarification-engine.md
6. execution-loop.md
7. roadmap.md

Core principle:
Go to sleep with an idea. Wake up with a project.
