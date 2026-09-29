import unittest

from processor.social_score import calcular_scores_posts


class TestSocialScore(unittest.TestCase):
    def test_shares_contribute_to_interaction_rate(self):
        posts = [
            {
                "id": "shared",
                "published_at": "2026-09-01T00:00:00Z",
                "views": 1000,
                "likes": 10,
                "comments": 10,
                "shares": 100,
            },
            {
                "id": "quiet",
                "published_at": "2026-09-01T00:00:00Z",
                "views": 1000,
                "likes": 10,
                "comments": 10,
                "shares": 0,
            },
        ]

        result = calcular_scores_posts(posts)

        self.assertEqual(result[0]["score"], 100.0)
        self.assertLess(result[1]["score"], result[0]["score"])

    def test_empty_and_zero_metrics_are_supported(self):
        self.assertEqual(calcular_scores_posts([]), [])
        posts = [{"id": "empty", "views": 0, "likes": 0, "comments": 0}]

        self.assertEqual(calcular_scores_posts(posts)[0]["score"], 0)

    def test_saves_and_clicks_contribute_to_interaction_rate(self):
        posts = [
            {"id": "active", "views": 100, "saves": 5, "clicks": 10},
            {"id": "quiet", "views": 100},
        ]

        calcular_scores_posts(posts)

        self.assertGreater(posts[0]["score"], posts[1]["score"])


if __name__ == "__main__":
    unittest.main()