import unittest
from unittest.mock import Mock, patch

from collectors.instagram import get_instagram_media
from collectors.linkedin import get_linkedin_posts


def api_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class TestInstagramCollector(unittest.TestCase):
    @patch("collectors.instagram.requests.get")
    def test_includes_media_and_insight_metrics(self, get):
        get.side_effect = [
            api_response({"data": [{
                "id": "media-1",
                "caption": "Reel de teste",
                "media_type": "VIDEO",
                "media_url": "https://example.test/reel.jpg",
                "permalink": "https://instagram.com/p/test",
                "timestamp": "2026-09-20T12:00:00+0000",
                "like_count": 25,
                "comments_count": 4,
            }]}),
            api_response({"data": [
                {"name": "views", "values": [{"value": 500}]},
                {"name": "shares", "values": [{"value": 12}]},
                {"name": "saved", "values": [{"value": 8}]},
            ]}),
        ]

        posts = get_instagram_media("token", "user-id")

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["views"], 500)
        self.assertEqual(posts[0]["shares"], 12)
        self.assertEqual(posts[0]["saves"], 8)
        self.assertEqual(posts[0]["comments"], 4)
        self.assertTrue(posts[0]["metric_availability"]["shares"])


class TestLinkedInCollector(unittest.TestCase):
    @patch("collectors.linkedin.requests.get")
    def test_includes_organization_post_statistics(self, get):
        get.side_effect = [
            api_response({"elements": [{
                "id": "urn:li:share:123",
                "commentary": "Lançamento",
                "publishedAt": 1789905600000,
            }]}),
            api_response({"elements": [{"totalShareStatistics": {
                "impressionCount": 900,
                "likeCount": 44,
                "commentCount": 7,
                "shareCount": 13,
                "clickCount": 21,
            }}]}),
        ]

        posts = get_linkedin_posts("token", "12345")

        self.assertEqual(posts[0]["views"], 900)
        self.assertEqual(posts[0]["likes"], 44)
        self.assertEqual(posts[0]["comments"], 7)
        self.assertEqual(posts[0]["shares"], 13)
        self.assertEqual(posts[0]["clicks"], 21)
        self.assertTrue(posts[0]["metrics_available"])


if __name__ == "__main__":
    unittest.main()