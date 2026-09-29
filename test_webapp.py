import unittest
from unittest.mock import patch

from webapp import refresh_social_data


class TestSocialDashboard(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()