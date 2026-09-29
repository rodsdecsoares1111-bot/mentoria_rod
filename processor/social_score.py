from datetime import datetime, timezone


def _days_since(published_at):
    try:
        published = datetime.fromisoformat(
            published_at.replace("Z", "+00:00")
        )
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        return max((datetime.now(timezone.utc) - published).days, 1)
    except (AttributeError, TypeError, ValueError):
        return 1


def calcular_scores_posts(posts):
    if not posts:
        return posts

    metrics = []
    for post in posts:
        views = max(int(post.get("views") or 0), 0)
        interactions = sum(
            max(int(post.get(metric) or 0), 0)
            for metric in ("likes", "shares", "saves", "clicks")
        )
        comments = max(int(post.get("comments") or 0), 0)
        metrics.append({
            "post": post,
            "views_per_day": views / _days_since(post.get("published_at")),
            "interaction_rate": interactions / views if views else 0,
            "comment_rate": comments / views if views else 0,
        })

    maxima = {
        "views_per_day": max(item["views_per_day"] for item in metrics),
        "interaction_rate": max(item["interaction_rate"] for item in metrics),
        "comment_rate": max(item["comment_rate"] for item in metrics),
    }
    weights = {
        "views_per_day": 0.40,
        "interaction_rate": 0.35,
        "comment_rate": 0.25,
    }

    for item in metrics:
        available_weight = sum(
            weight for metric, weight in weights.items() if maxima[metric] > 0
        )
        points = sum(
            item[metric] / maxima[metric] * weight
            for metric, weight in weights.items()
            if maxima[metric] > 0
        )
        item["post"]["score"] = round(
            points / available_weight * 100 if available_weight else 0,
            1,
        )

    return posts