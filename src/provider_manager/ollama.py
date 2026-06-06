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
        raise NotImplementedError()

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def stream(self, prompt: str, **kwargs):
        raise NotImplementedError()

    def embeddings(self, texts: List[str], **kwargs) -> List[float]:
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
