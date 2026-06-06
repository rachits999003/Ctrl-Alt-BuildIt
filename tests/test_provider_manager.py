import json
from unittest.mock import patch, MagicMock
from src.provider_manager.manager import ProviderManager
from src.provider_manager.ollama import OllamaProvider


def test_from_config_loads_providers(tmp_path, monkeypatch):
    cfg = {
        "local_ollama": {"type": "ollama", "base_url": "http://127.0.0.1:11434"}
    }
    cfg_path = tmp_path / "providers.json"
    cfg_path.write_text(json.dumps(cfg))

    pm = ProviderManager.from_config(str(cfg_path))
    assert "local_ollama" in pm.list_providers()
    p = pm.get("local_ollama")
    assert isinstance(p, OllamaProvider)


def test_provider_health_check_monkeypatched(monkeypatch):
    p = OllamaProvider()
    class Resp:
        status_code = 200

    monkeypatch.setattr("src.provider_manager.ollama.requests.get", lambda *args, **kwargs: Resp())
    assert p.health_check() is True
