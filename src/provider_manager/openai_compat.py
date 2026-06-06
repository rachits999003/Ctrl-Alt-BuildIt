import os
import requests
from typing import Any, Dict, List

from .base import Provider


class OpenAICompatibleProvider(Provider):
    def __init__(self, base_url: str, api_key: str = None, model: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def generate(self, prompt: str, **kwargs) -> str:
        payload = {"model": self.model, "prompt": prompt}
        resp = requests.post(f"{self.base_url}/v1/completions", json=payload, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        j = resp.json()
        # best-effort extraction
        return j.get("choices", [{}])[0].get("text", "")

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        payload = {"model": self.model, "messages": messages}
        resp = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def stream(self, prompt: str, **kwargs):
        # Streaming not implemented in the MVP skeleton
        raise NotImplementedError()

    def embeddings(self, texts: List[str], **kwargs) -> List[float]:
        payload = {"model": self.model, "input": texts}
        resp = requests.post(f"{self.base_url}/v1/embeddings", json=payload, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        j = resp.json()
        return j.get("data", [])

    def tool_calls(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def health_check(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/v1/models", headers=self._headers(), timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def model_info(self) -> Dict[str, Any]:
        return {"provider": "openai_compatible", "base_url": self.base_url, "model": self.model}
