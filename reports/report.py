class Report:
    """Responsável por montar o texto final do relatório de performance dos vídeos."""

    def gerar_texto(self, videos):
        """Gera uma string legível com os totais e o desempenho individual de cada vídeo."""
        linhas = [
            "MENTORIA - RELATÓRIO DO YOUTUBE",
            "=" * 60,
            f"Vídeos encontrados: {len(videos)}",
            "",
        ]

        visualizacoes = sum(
            video.visualizacoes
            for video in videos
        )

        curtidas = sum(
            video.curtidas
            for video in videos
        )

        comentarios = sum(
            video.comentarios
            for video in videos
        )

        linhas.extend([
            f"Visualizações: {visualizacoes}",
            f"Curtidas: {curtidas}",
            f"Comentários: {comentarios}",
            "",
            "VÍDEOS",
            "",
        ])

        for video in videos:
            # A classificação serve para ler rapidamente se o desempenho é excelente, bom, médio ou baixo.
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
        """Cria o relatório e imprime no console para facilitar a visualização direta."""
        texto = self.gerar_texto(videos)

        print()
        print(texto)

        return texto
