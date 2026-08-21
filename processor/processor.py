class Processor:

    def processar(self, videos):

        for video in videos:

            video.titulo = (
                video.titulo.strip()
            )

            video.descricao = (
                video.descricao.strip()
            )

        return videos
