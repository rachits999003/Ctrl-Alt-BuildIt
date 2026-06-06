import json
import os
from typing import Dict, Optional

from .manager import ProviderManager


class RoutingConfig:
    def __init__(self, path: Optional[str] = None):
        path = path or os.path.join(os.getcwd(), "config", "routing.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.cfg = json.load(f)
        else:
            self.cfg = {}

    def get_provider_for_task(self, task_type: str) -> Optional[str]:
        # Exact match or fallback to "default"
        return self.cfg.get(task_type) or self.cfg.get("default")


class Router:
    def __init__(self, provider_manager: Optional[ProviderManager] = None, cfg_path: Optional[str] = None):
        self.pm = provider_manager or ProviderManager.from_config()
        self.cfg = RoutingConfig(cfg_path)

    def select_provider(self, task_type: str):
        name = self.cfg.get_provider_for_task(task_type)
        if not name:
            # fallback to first healthy provider
            for p in self.pm.list_providers():
                pr = self.pm.get(p)
                try:
                    if pr.health_check():
                        return p
                except Exception:
                    continue
            return None
        # ensure provider exists and is healthy
        p = self.pm.get(name)
        if not p:
            return None
        try:
            if p.health_check():
                return name
        except Exception:
            return None
