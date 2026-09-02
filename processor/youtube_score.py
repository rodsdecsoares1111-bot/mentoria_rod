from datetime import datetime, timezone


def calcular_dias_publicado(data_publicacao):

    try:
        data = datetime.fromisoformat(
            data_publicacao.replace(
                "Z",
                "+00:00"
            )
        )

        agora = datetime.now(timezone.utc)

        return max(
            (agora - data).days,
            1
        )

    except (ValueError, AttributeError):

        return 1


def calcular_scores(videos):

    if not videos:
        return videos

    metricas = []

    for video in videos:

        dias = calcular_dias_publicado(
            video.data_publicacao
        )

        visualizacoes_por_dia = (
            video.visualizacoes / dias
        )

        if video.visualizacoes > 0:

            taxa_curtidas = (
                video.curtidas
                / video.visualizacoes
            )

            taxa_comentarios = (
                video.comentarios
                / video.visualizacoes
            )

        else:

            taxa_curtidas = 0
            taxa_comentarios = 0

        metricas.append({
            "video": video,
            "visualizacoes_por_dia":
                visualizacoes_por_dia,
            "taxa_curtidas":
                taxa_curtidas,
            "taxa_comentarios":
                taxa_comentarios
        })

    maior_visualizacoes_dia = max(
        item["visualizacoes_por_dia"]
        for item in metricas
    )

    maior_taxa_curtidas = max(
        item["taxa_curtidas"]
        for item in metricas
    )

    maior_taxa_comentarios = max(
        item["taxa_comentarios"]
        for item in metricas
    )

    for item in metricas:

        pontos = 0
        peso_disponivel = 0

        if maior_visualizacoes_dia > 0:

            pontos += (
                item["visualizacoes_por_dia"]
                / maior_visualizacoes_dia
            ) * 0.40

            peso_disponivel += 0.40

        if maior_taxa_curtidas > 0:

            pontos += (
                item["taxa_curtidas"]
                / maior_taxa_curtidas
            ) * 0.35

            peso_disponivel += 0.35

        if maior_taxa_comentarios > 0:

            pontos += (
                item["taxa_comentarios"]
                / maior_taxa_comentarios
            ) * 0.25

            peso_disponivel += 0.25

        if peso_disponivel > 0:

            score = (
                pontos
                / peso_disponivel
            ) * 100

        else:

            score = 0

        item["video"].score = round(
            score,
            1
        )

    return videos