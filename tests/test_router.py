from src.provider_manager.manager import ProviderManager
from src.provider_manager.router import Router


def test_router_selects_default(monkeypatch, tmp_path):
    # create a fake providers.json
    cfg = {"local_ollama": {"type": "ollama", "base_url": "http://127.0.0.1:11434"}}
    cfg_path = tmp_path / "providers.json"
    cfg_path.write_text(__import__('json').dumps(cfg))

    pm = ProviderManager.from_config(str(cfg_path))

    # monkeypatch health_check to True
    for name in pm.list_providers():
        p = pm.get(name)
        monkeypatch.setattr(p, "health_check", lambda: True)

    router = Router(provider_manager=pm, cfg_path=str(tmp_path / "routing.json"))
    # no routing.json exists, should pick first healthy provider
    sel = router.select_provider("implementation")
    assert sel in pm.list_providers()
