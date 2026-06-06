from unittest.mock import patch, MagicMock
from src.provider_manager.openai_compat import OpenAICompatibleProvider


def test_openai_generate(monkeypatch):
    p = OpenAICompatibleProvider(base_url="http://example.com", api_key="key", model="m")

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"text": "hello"}]}

    monkeypatch.setattr("src.provider_manager.openai_compat.requests.post", lambda *args, **kwargs: Resp())
    out = p.generate("hi")
    assert out == "hello"
