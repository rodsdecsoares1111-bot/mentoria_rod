class Report:
    def gerar_texto(self, videos):
        linhas = [
            "MENTORIA - RELATÓRIO DO YOUTUBE",
            "=" * 60,
            f"Vídeos encontrados: {len(videos)}",
            "",
        ]

        visualizacoes = sum(video.visualizacoes for video in videos)
        curtidas = sum(video.curtidas for video in videos)
        comentarios = sum(video.comentarios for video in videos)

        linhas.extend([
            f"Visualizações: {visualizacoes}",
            f"Curtidas: {curtidas}",
            f"Comentários: {comentarios}",
            "",
            "VÍDEOS",
            "",
        ])

        for video in videos:
            if video.score >= 80:
                classificacao = "Excelente"
            elif video.score >= 60:
                classificacao = "Bom"
            elif video.score >= 40:
                classificacao = "Médio"
            else:
                classificacao = "Baixo"

            linhas.extend([
                "-" * 60,
                f"Título: {video.titulo}",
                f"Visualizações: {video.visualizacoes}",
                f"Curtidas: {video.curtidas}",
                f"Comentários: {video.comentarios}",
                f"URL: {video.url}",
                f"Score: {video.score}/100",
                f"Classificação: {classificacao}",
                "",
            ])

        return "\n".join(linhas)

    def gerar(self, videos):
        texto = self.gerar_texto(videos)
        print()
        print(texto)
        return texto