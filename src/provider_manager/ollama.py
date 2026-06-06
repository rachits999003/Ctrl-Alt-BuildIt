import requests
from typing import Any, Dict, List

from .base import Provider


class OllamaProvider(Provider):
    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")

    def discover_models(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=2.0)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return []

    def generate(self, prompt: str, **kwargs) -> str:
        # Best-effort: call Ollama's completions endpoint if available
        model = kwargs.get("model")
        payload = {"model": model, "prompt": prompt}
        try:
            resp = requests.post(f"{self.base_url}/v1/completions", json=payload, timeout=10)
            resp.raise_for_status()
            j = resp.json()
            return j.get("choices", [{}])[0].get("text", "")
        except Exception:
            raise NotImplementedError()

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        # Best-effort Chat support — Ollama compatibility may vary.
        model = kwargs.get("model")
        payload = {"model": model, "messages": messages}
        try:
            resp = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            raise NotImplementedError()

    def stream(self, prompt: str, **kwargs):
        raise NotImplementedError()

    def embeddings(self, texts: List[str], **kwargs) -> List[float]:
        # Ollama may not support embeddings via this endpoint; raise to signal lack.
        raise NotImplementedError()

    def tool_calls(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def health_check(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=1.0)
            return resp.status_code == 200
        except Exception:
            return False

    def model_info(self) -> Dict[str, Any]:
        return {"provider": "ollama", "base_url": self.base_url}
