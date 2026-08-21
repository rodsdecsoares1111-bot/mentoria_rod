import requests

from config import (
    YOUTUBE_API_KEY,
    YOUTUBE_CHANNEL_ID
)

from models.video import Video

class YouTubeCollector:

    BASE_URL = (
        "https://www.googleapis.com/"
        "youtube/v3"
    )

    def __init__(self):

        self.api_key = YOUTUBE_API_KEY

        self.channel_id = YOUTUBE_CHANNEL_ID

    def obter_playlist_uploads(self):

        url = (
            f"{self.BASE_URL}/channels"
        )

        params = {

            "part": "contentDetails",

            "id": self.channel_id,

            "key": self.api_key

        }

        response = requests.get(
            url,
            params=params
        )

        if response.status_code != 200:

            raise Exception(
                "Erro ao buscar canal:\n"
                f"{response.text}"
            )

        data = response.json()

        if not data.get("items"):

            raise Exception(
                "Canal não encontrado."
            )

        playlist_id = (
            data["items"][0]
            ["contentDetails"]
            ["relatedPlaylists"]
            ["uploads"]
        )

        return playlist_id

    def obter_ids_videos(
        self,
        playlist_id,
        quantidade=10
    ):

        url = (
            f"{self.BASE_URL}/playlistItems"
        )

        params = {

            "part": "contentDetails",

            "playlistId": playlist_id,

            "maxResults": quantidade,

            "key": self.api_key

        }

        response = requests.get(
            url,
            params=params
        )

        if response.status_code != 200:

            raise Exception(
                "Erro ao buscar vídeos:\n"
                f"{response.text}"
            )

        data = response.json()

        ids = []

        for item in data.get("items", []):

            video_id = (
                item["contentDetails"]
                ["videoId"]
            )

            ids.append(video_id)

        return ids

    def obter_dados_videos(
        self,
        video_ids
    ):

        if not video_ids:

            return []

        url = (
            f"{self.BASE_URL}/videos"
        )

        params = {

            "part": (
                "snippet,"
                "contentDetails,"
                "statistics"
            ),

            "id": ",".join(video_ids),

            "key": self.api_key

        }

        response = requests.get(
            url,
            params=params
        )

        if response.status_code != 200:

            raise Exception(
                "Erro ao buscar dados dos vídeos:\n"
                f"{response.text}"
            )

        return response.json().get(
            "items",
            []
        )

    def coletar_videos(
        self,
        quantidade=10
    ):

        print(
            "Buscando playlist de uploads..."
        )

        playlist_id = (
            self.obter_playlist_uploads()
        )

        print(
            f"Playlist encontrada: "
            f"{playlist_id}"
        )

        print(
            "Buscando vídeos..."
        )

        video_ids = (
            self.obter_ids_videos(
                playlist_id,
                quantidade
            )
        )

        print(
            f"{len(video_ids)} vídeos encontrados."
        )

        dados = (
            self.obter_dados_videos(
                video_ids
            )
        )

        videos = []

        for item in dados:

            snippet = item.get(
                "snippet",
                {}
            )

            statistics = item.get(
                "statistics",
                {}
            )

            content = item.get(
                "contentDetails",
                {}
            )

            video = Video(

                id=item["id"],

                titulo=snippet.get(
                    "title",
                    ""
                ),

                descricao=snippet.get(
                    "description",
                    ""
                ),

                url=(
                    "https://www.youtube.com/watch?v="
                    + item["id"]
                ),

                data_publicacao=snippet.get(
                    "publishedAt",
                    ""
                ),

                thumbnail=(
                    snippet
                    .get("thumbnails", {})
                    .get("high", {})
                    .get("url", "")
                ),

                duracao=content.get(
                    "duration",
                    ""
                ),

                visualizacoes=int(
                    statistics.get(
                        "viewCount",
                        0
                    )
                ),

                curtidas=int(
                    statistics.get(
                        "likeCount",
                        0
                    )
                ),

                comentarios=int(
                    statistics.get(
                        "commentCount",
                        0
                    )
                )
            )

            videos.append(video)

        return videos
