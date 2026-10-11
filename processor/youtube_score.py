from datetime import datetime, timezone


def calcular_dias_publicado(data_publicacao):
    try:
        data = datetime.fromisoformat(data_publicacao.replace("Z", "+00:00"))
        agora = datetime.now(timezone.utc)
        return max((agora - data).days, 1)
    except (ValueError, AttributeError):
        return 1


def calcular_scores(videos):
    if not videos:
        return videos

    metricas = []
    for video in videos:
        dias = calcular_dias_publicado(video.data_publicacao)
        visualizacoes_por_dia = video.visualizacoes / dias
        if video.visualizacoes > 0:
            taxa_curtidas = video.curtidas / video.visualizacoes
            taxa_comentarios = video.comentarios / video.visualizacoes
        else:
            taxa_curtidas = 0
            taxa_comentarios = 0

        metricas.append({
            "video": video,
            "visualizacoes_por_dia": visualizacoes_por_dia,
            "taxa_curtidas": taxa_curtidas,
            "taxa_comentarios": taxa_comentarios,
        })

    maiores = {
        chave: max(item[chave] for item in metricas)
        for chave in ("visualizacoes_por_dia", "taxa_curtidas", "taxa_comentarios")
    }
    pesos = {
        "visualizacoes_por_dia": 0.40,
        "taxa_curtidas": 0.35,
        "taxa_comentarios": 0.25,
    }

    for item in metricas:
        peso_disponivel = sum(peso for chave, peso in pesos.items() if maiores[chave] > 0)
        pontos = sum(
            item[chave] / maiores[chave] * peso
            for chave, peso in pesos.items()
            if maiores[chave] > 0
        )
        item["video"].score = round(
            pontos / peso_disponivel * 100 if peso_disponivel else 0,
            1,
        )

    return videos