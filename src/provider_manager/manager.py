import json
import os
from typing import Dict, Optional

from .base import Provider
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatibleProvider


class ProviderManager:
    def __init__(self):
        self._providers: Dict[str, Provider] = {}

    def register(self, name: str, provider: Provider):
        self._providers[name] = provider

    def get(self, name: str) -> Optional[Provider]:
        return self._providers.get(name)

    def list_providers(self):
        return list(self._providers.keys())

    @classmethod
    def from_config(cls, path: str = None):
        pm = cls()
        path = path or os.path.join(os.getcwd(), "config", "providers.json")
        if not os.path.exists(path):
            return pm
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for name, c in cfg.items():
            ptype = c.get("type")
            if ptype == "ollama":
                pm.register(name, OllamaProvider(base_url=c.get("base_url", "http://127.0.0.1:11434")))
            elif ptype in ("openai", "openai_compatible"):
                pm.register(name, OpenAICompatibleProvider(base_url=c["base_url"], api_key=c.get("api_key"), model=c.get("model")))
        return pm
