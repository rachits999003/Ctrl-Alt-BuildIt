"""
Tests for provider_manager — runs fully offline using unittest.mock.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.provider_manager.manager import ProviderManager
from src.provider_manager.ollama import OllamaProvider
from src.provider_manager.openai_compat import OpenAICompatibleProvider


# ── OllamaProvider ────────────────────────────────────────────────

class TestOllamaProviderHealthCheck(unittest.TestCase):
    @patch("src.provider_manager.ollama.requests.get")
    def test_health_check_ok(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        p = OllamaProvider()
        self.assertTrue(p.health_check())

    @patch("src.provider_manager.ollama.requests.get", side_effect=Exception("conn refused"))
    def test_health_check_down(self, _):
        p = OllamaProvider()
        self.assertFalse(p.health_check())

    def test_model_info(self):
        p = OllamaProvider(base_url="http://localhost:11434")
        info = p.model_info()
        self.assertEqual(info["provider"], "ollama")
        self.assertIn("base_url", info)

    @patch("src.provider_manager.ollama.requests.get")
    def test_discover_models_ok(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = {"models": ["llama3"]}
        p = OllamaProvider()
        result = p.discover_models()
        self.assertIn("models", result)

    @patch("src.provider_manager.ollama.requests.get", side_effect=Exception("timeout"))
    def test_discover_models_failure_returns_empty(self, _):
        p = OllamaProvider()
        self.assertEqual(p.discover_models(), [])

    def test_unimplemented_stubs_raise(self):
        p = OllamaProvider()
        with self.assertRaises(NotImplementedError): p.generate("hi")
        with self.assertRaises(NotImplementedError): p.chat([])
        with self.assertRaises(NotImplementedError): p.stream("hi")
        with self.assertRaises(NotImplementedError): p.embeddings(["hi"])
        with self.assertRaises(NotImplementedError): p.tool_calls()


# ── OpenAICompatibleProvider ──────────────────────────────────────

class TestOpenAICompatProvider(unittest.TestCase):
    def _provider(self):
        return OpenAICompatibleProvider(
            base_url="https://api.example.com", api_key="test-key", model="gpt-test"
        )

    def test_model_info(self):
        p = self._provider()
        info = p.model_info()
        self.assertEqual(info["provider"], "openai_compatible")
        self.assertEqual(info["model"], "gpt-test")

    @patch("src.provider_manager.openai_compat.requests.get")
    def test_health_check_ok(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        self.assertTrue(self._provider().health_check())

    @patch("src.provider_manager.openai_compat.requests.get", side_effect=Exception("err"))
    def test_health_check_fail(self, _):
        self.assertFalse(self._provider().health_check())

    @patch("src.provider_manager.openai_compat.requests.post")
    def test_generate(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "choices": [{"text": "Hello!"}]
        }
        result = self._provider().generate("Say hello")
        self.assertEqual(result, "Hello!")

    @patch("src.provider_manager.openai_compat.requests.post")
    def test_chat(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
        }
        result = self._provider().chat([{"role": "user", "content": "Hey"}])
        self.assertIn("choices", result)

    @patch("src.provider_manager.openai_compat.requests.post")
    def test_embeddings(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.json.return_value = {"data": [[0.1, 0.2]]}
        result = self._provider().embeddings(["hello"])
        self.assertEqual(result, [[0.1, 0.2]])

    def test_stream_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self._provider().stream("hi")

    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            p = OpenAICompatibleProvider(base_url="https://api.example.com")
            self.assertEqual(p.api_key, "env-key")

    def test_auth_header_present(self):
        p = self._provider()
        headers = p._headers()
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))


# ── ProviderManager ───────────────────────────────────────────────

class TestProviderManager(unittest.TestCase):
    def test_register_and_get(self):
        pm = ProviderManager()
        mock_p = MagicMock()
        pm.register("mock", mock_p)
        self.assertIs(pm.get("mock"), mock_p)

    def test_get_missing_returns_none(self):
        pm = ProviderManager()
        self.assertIsNone(pm.get("nonexistent"))

    def test_list_providers(self):
        pm = ProviderManager()
        pm.register("a", MagicMock())
        pm.register("b", MagicMock())
        self.assertEqual(sorted(pm.list_providers()), ["a", "b"])

    def test_from_config_missing_file_returns_empty(self):
        pm = ProviderManager.from_config("/nonexistent/path/providers.json")
        self.assertEqual(pm.list_providers(), [])

    def test_from_config_ollama(self):
        cfg = {"my_ollama": {"type": "ollama", "base_url": "http://localhost:11434"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            fname = f.name
        try:
            pm = ProviderManager.from_config(fname)
            self.assertIn("my_ollama", pm.list_providers())
            self.assertIsInstance(pm.get("my_ollama"), OllamaProvider)
        finally:
            os.unlink(fname)

    def test_from_config_openai_compat(self):
        cfg = {
            "my_openai": {
                "type": "openai_compatible",
                "base_url": "https://api.example.com",
                "api_key": "key123",
                "model": "gpt-4",
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            fname = f.name
        try:
            pm = ProviderManager.from_config(fname)
            self.assertIn("my_openai", pm.list_providers())
            p = pm.get("my_openai")
            self.assertIsInstance(p, OpenAICompatibleProvider)
            self.assertEqual(p.model, "gpt-4")
        finally:
            os.unlink(fname)

    def test_from_config_unknown_type_is_skipped(self):
        cfg = {"weird": {"type": "unknown_provider"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(cfg, f)
            fname = f.name
        try:
            pm = ProviderManager.from_config(fname)
            self.assertEqual(pm.list_providers(), [])
        finally:
            os.unlink(fname)


if __name__ == "__main__":
    unittest.main(verbosity=2)
