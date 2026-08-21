import requests


def get_instagram_media(access_token, instagram_user_id):
    url = f"https://graph.facebook.com/vXX.X/{instagram_user_id}/media"

    params = {
        "fields": "id,caption,media_type,media_url,permalink,timestamp",
        "access_token": access_token,
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()["data"]
