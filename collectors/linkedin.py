from datetime import datetime, timezone

import requests


def get_linkedin_posts(access_token, organization_id, api_version="202601"):
    organization_urn = organization_id
    if not organization_urn.startswith("urn:"):
        organization_urn = f"urn:li:organization:{organization_urn}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": api_version,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    response = requests.get(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        params={"q": "author", "author": organization_urn, "count": 50},
        timeout=30,
    )
    response.raise_for_status()

    posts = []
    for item in response.json().get("elements", []):
        post_id = item.get("id", "")
        stats = {}
        metrics_available = False
        if post_id:
            try:
                stats_response = requests.get(
                    "https://api.linkedin.com/rest/organizationalEntityShareStatistics",
                    headers=headers,
                    params={
                        "q": "organizationalEntity",
                        "organizationalEntity": organization_urn,
                        "shares[0]": post_id,
                    },
                    timeout=30,
                )
                stats_response.raise_for_status()
                elements = stats_response.json().get("elements", [])
                stats = elements[0].get("totalShareStatistics", {}) if elements else {}
                metrics_available = bool(stats)
            except requests.RequestException:
                pass

        content = item.get("commentary", "")
        if isinstance(content, dict):
            content = content.get("text", "")
        if not content:
            content = "Publicação do LinkedIn"

        created_at = item.get("publishedAt") or item.get("createdAt") or 0
        if created_at:
            created_at = created_at / 1000
            created_at = datetime.fromtimestamp(created_at, timezone.utc).isoformat()

        posts.append({
            "id": post_id,
            "platform": "linkedin",
            "title": str(content).strip(),
            "url": f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else "",
            "media_type": "Publicação",
            "thumbnail": "",
            "published_at": created_at,
            "views": stats.get("impressionCount", 0),
            "reach": 0,
            "likes": stats.get("likeCount", 0),
            "comments": stats.get("commentCount", 0),
            "shares": stats.get("shareCount", 0),
            "saves": 0,
            "clicks": stats.get("clickCount", 0),
            "metrics_available": metrics_available,
            "metric_availability": {
                "views": "impressionCount" in stats,
                "reach": False,
                "likes": "likeCount" in stats,
                "comments": "commentCount" in stats,
                "shares": "shareCount" in stats,
                "saves": False,
                "clicks": "clickCount" in stats,
            },
        })

    return posts
