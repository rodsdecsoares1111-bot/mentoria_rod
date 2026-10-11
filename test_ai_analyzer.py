import os
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai.analyzer import AIAnalyzer


class TestSocialPostAnalyzer(unittest.TestCase):
    def test_analyzes_caption_and_metrics_with_configured_model(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content="Teste um CTA mais específico.")
            )]
        )
        post = {
            "platform": "instagram",
            "media_type": "REEL",
            "title": "Bastidores do projeto",
            "published_at": "2026-09-20T12:00:00Z",
            "score": 76.5,
            "views": 1200,
            "likes": 95,
            "comments": 12,
            "shares": 8,
            "saves": 4,
            "clicks": 0,
        }

        with patch.dict(os.environ, {"OPENAI_MODEL": "test-model"}):
            analyzer = AIAnalyzer(client=client)
            tip = analyzer.analisar_post_social(post)

        self.assertEqual(tip, "Teste um CTA mais específico.")
        call = client.chat.completions.create.call_args.kwargs
        self.assertEqual(call["model"], "test-model")
        self.assertIn("Bastidores do projeto", call["messages"][1]["content"])
        self.assertIn("compartilhamentos", call["messages"][1]["content"])

    def test_requires_api_key_when_creating_real_client(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                AIAnalyzer()

    def test_unavailable_metrics_are_sent_as_null_not_zero(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Teste outro formato."))]
        )
        post = {
            "platform": "linkedin",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "metric_availability": {
                "views": False,
                "likes": False,
                "comments": False,
                "shares": False,
            },
        }

        AIAnalyzer(client=client).analisar_post_social(post)

        prompt_data = json.loads(client.chat.completions.create.call_args.kwargs["messages"][1]["content"])
        self.assertIsNone(prompt_data["metricas"]["visualizacoes_ou_impressoes"])
        self.assertIsNone(prompt_data["metricas"]["curtidas"])


if __name__ == "__main__":
    unittest.main()