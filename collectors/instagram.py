import requests


def get_instagram_media(
    access_token,
    instagram_user_id,
    api_version="v22.0"
):
    url = (
        f"https://graph.facebook.com/{api_version}/"
        f"{instagram_user_id}/media"
    )

    params = {
        "fields": (
            "id,caption,media_type,media_url,permalink,timestamp,"
            "like_count,comments_count,thumbnail_url"
        ),
        "access_token": access_token,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    media_items = response.json().get("data", [])
    posts = []

    for media in media_items:
        insights_available = False
        metrics = {
            "views": media.get("views") or media.get("play_count") or 0,
            "reach": 0,
            "shares": 0,
            "saves": 0,
        }
        insights_url = (
            f"https://graph.facebook.com/{api_version}/"
            f"{media['id']}/insights"
        )
        try:
            insights_response = requests.get(
                insights_url,
                params={
                    "metric": "views,reach,shares,saved,total_interactions",
                    "access_token": access_token,
                },
                timeout=30,
            )
            insights_response.raise_for_status()
            insights = insights_response.json().get("data", [])
            insights_available = bool(insights)
            for insight in insights:
                values = insight.get("values") or []
                value = values[0].get("value", 0) if values else insight.get("value", 0)
                metric_name = insight.get("name")
                if metric_name == "views":
                    metrics["views"] = value
                elif metric_name == "reach":
                    metrics["reach"] = value
                elif metric_name == "shares":
                    metrics["shares"] = value
                elif metric_name == "saved":
                    metrics["saves"] = value
        except requests.RequestException:
            pass

        posts.append({
            "id": media.get("id", ""),
            "platform": "instagram",
            "title": (media.get("caption") or "").strip() or "Publicação sem legenda",
            "url": media.get("permalink", ""),
            "media_type": media.get("media_type", "Post"),
            "thumbnail": media.get("thumbnail_url") or media.get("media_url", ""),
            "published_at": media.get("timestamp", ""),
            "views": metrics["views"],
            "reach": metrics["reach"],
            "likes": media.get("like_count", 0),
            "comments": media.get("comments_count", 0),
            "shares": metrics["shares"],
            "saves": metrics["saves"],
            "clicks": 0,
            "metrics_available": insights_available,
            "metric_availability": {
                "views": insights_available and any(item.get("name") == "views" for item in insights),
                "reach": insights_available and any(item.get("name") == "reach" for item in insights),
                "likes": media.get("like_count") is not None,
                "comments": media.get("comments_count") is not None,
                "shares": insights_available and any(item.get("name") == "shares" for item in insights),
                "saves": insights_available and any(item.get("name") == "saved" for item in insights),
                "clicks": False,
            },
        })

    return posts
