from datetime import datetime, timezone

# Este módulo calcula o "score" de cada vídeo com base em engajamento.
# Ele transforma dados brutos como visualizações, curtidas e comentários em um valor comparável.


def calcular_dias_publicado(data_publicacao):
    """Converte a data de publicação em um número de dias, evitando divisão por zero."""
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
        # Se a data vier vazia ou inválida, assume 1 dia para manter a lógica estável.
        return 1


def calcular_scores(videos):
    """Calcula e atribui um score para cada vídeo conforme sua performance relativa."""
    if not videos:
        return videos

    metricas = []

    for video in videos:
        # Ajusta as métricas por tempo de publicação para comparar vídeos mais antigos e novos de forma justa.
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
            "visualizacoes_por_dia": visualizacoes_por_dia,
            "taxa_curtidas": taxa_curtidas,
            "taxa_comentarios": taxa_comentarios
        })

    # Identifica os maiores valores dentro do conjunto para normalizar o score.
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
        # Cada métrica pesa na nota final com soma de 100% de pesos.
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

        item["video"].score = round(score, 1)

    return videos