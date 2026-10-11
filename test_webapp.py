import http.client
import json
import threading
import unittest
from unittest.mock import patch

from http.server import ThreadingHTTPServer

from webapp import (
    AIConfigurationError,
    DashboardHandler,
    analyze_social_post,
    load_demo_data,
    refresh_social_data,
)


class TestSocialDashboard(unittest.TestCase):
    def test_demo_data_can_be_loaded_before_api_refresh(self):
        data = load_demo_data()

        self.assertTrue(data["demo"])
        self.assertEqual(len(data["posts"]), 6)
        self.assertTrue(data["updated_at"])

    def test_refresh_uses_demo_posts_when_no_social_credentials_are_configured(self):
        with patch("webapp._credentials_status", return_value={"instagram": False, "linkedin": False}):
            data = refresh_social_data()

        self.assertTrue(data["demo"])
        self.assertEqual(len(data["posts"]), 6)
        self.assertEqual({post["platform"] for post in data["posts"]}, {"instagram", "linkedin"})
        self.assertEqual(data["platforms"]["instagram"]["state"], "demo")
        self.assertEqual(data["platforms"]["linkedin"]["state"], "demo")

    def test_refresh_combines_instagram_and_linkedin(self):
        instagram_posts = [{
            "id": "ig-1",
            "platform": "instagram",
            "title": "Instagram post",
            "published_at": "2026-09-01T00:00:00Z",
            "views": 1000,
            "likes": 100,
            "comments": 20,
            "shares": 10,
            "saves": 5,
            "clicks": 0,
            "metrics_available": True,
        }]
        linkedin_posts = [{
            "id": "li-1",
            "platform": "linkedin",
            "title": "LinkedIn post",
            "published_at": "2026-09-01T00:00:00Z",
            "views": 500,
            "likes": 10,
            "comments": 1,
            "shares": 1,
            "saves": 0,
            "clicks": 2,
            "metrics_available": True,
        }]

        with (
            patch("webapp._credentials_status", return_value={"instagram": True, "linkedin": True}),
            patch("webapp.get_instagram_media", return_value=instagram_posts),
            patch("webapp.get_linkedin_posts", return_value=linkedin_posts),
        ):
            data = refresh_social_data()

        self.assertEqual({post["platform"] for post in data["posts"]}, {"instagram", "linkedin"})
        self.assertEqual(data["platforms"]["instagram"]["count"], 1)
        self.assertEqual(data["platforms"]["linkedin"]["count"], 1)
        instagram = next(post for post in data["posts"] if post["platform"] == "instagram")
        linkedin = next(post for post in data["posts"] if post["platform"] == "linkedin")
        self.assertEqual(instagram["score"], 100.0)
        self.assertLess(linkedin["score"], instagram["score"])

    def test_api_failure_message_does_not_expose_token(self):
        with (
            patch("webapp._credentials_status", return_value={"instagram": True, "linkedin": False}),
            patch("webapp.get_instagram_media", side_effect=RuntimeError("token=secret")),
        ):
            data = refresh_social_data()

        self.assertEqual(data["platforms"]["instagram"]["state"], "error")
        self.assertNotIn("secret", data["platforms"]["instagram"]["message"])

    def test_ai_analyzes_the_selected_collected_post_and_caches_result(self):
        post = {
            "id": "ig-1",
            "platform": "instagram",
            "title": "Bastidores do projeto",
            "views": 600,
            "score": 72.0,
        }
        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("webapp.POSTS", [post]),
            patch("webapp.AI_TIPS", {}),
            patch("webapp.AIAnalyzer") as analyzer_class,
        ):
            analyzer_class.return_value.analisar_post_social.return_value = "Teste um CTA claro."

            first = analyze_social_post("ig-1", "instagram")
            second = analyze_social_post("ig-1", "instagram")

        self.assertEqual(first["tip"], "Teste um CTA claro.")
        self.assertEqual(second, first)
        analyzer_class.return_value.analisar_post_social.assert_called_once_with(post)

    def test_ai_requires_key_and_a_post_from_the_current_collection(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(AIConfigurationError):
                analyze_social_post("ig-1", "instagram")

        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("webapp.POSTS", []),
        ):
            with self.assertRaises(LookupError):
                analyze_social_post("missing", "instagram")

    def test_analyze_http_route_returns_tip_for_selected_post(self):
        post = {
            "id": "li-7",
            "platform": "linkedin",
            "title": "Lançamento do projeto",
            "views": 800,
            "score": 64.0,
        }
        server = ThreadingHTTPServer(("127.0.0.1", 0), DashboardHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)

        with (
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
            patch("webapp.POSTS", [post]),
            patch("webapp.AI_TIPS", {}),
            patch("webapp.AIAnalyzer") as analyzer_class,
        ):
            analyzer_class.return_value.analisar_post_social.return_value = "Teste um início mais direto."
            thread.start()
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_address[1], timeout=5
            )
            try:
                connection.request(
                    "POST",
                    "/api/analyze",
                    body=json.dumps({"post_id": "li-7", "platform": "linkedin"}),
                    headers={"Content-Type": "application/json"},
                )
                response = connection.getresponse()
                payload = json.loads(response.read())
            finally:
                connection.close()
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["tip"], "Teste um início mais direto.")
        analyzer_class.return_value.analisar_post_social.assert_called_once_with(post)


if __name__ == "__main__":
    unittest.main()