import os

from dotenv import load_dotenv

from collectors.youtube import (
    YouTubeCollector
)

from processor.youtube_score import (
    calcular_scores
)

from notifications.email import (
    enviar_relatorio
)

from reports.report import (
    Report
)

load_dotenv()

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
EMAIL_SENHA = os.getenv("EMAIL_SENHA")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")
EMAIL_SMTP_SERVIDOR = os.getenv(
    "EMAIL_SMTP_SERVIDOR",
    "smtp.gmail.com"
)
EMAIL_SMTP_PORTA = os.getenv(
    "EMAIL_SMTP_PORTA",
    "465"
)


def main():

    collector = YouTubeCollector()

    videos = collector.coletar_videos(
        quantidade=5
    )

    videos = calcular_scores(videos)

    for video in videos:

        print()
        print("=" * 50)

        print(
            f"Título: {video.titulo}"
        )

        print(
            f"Visualizações: "
            f"{video.visualizacoes}"
        )

        print(
            f"Curtidas: "
            f"{video.curtidas}"
        )

        print(
            f"Comentários: "
            f"{video.comentarios}"
        )

        print(
            f"URL: {video.url}"
        )

        print(
            f"Score: {video.score}/100"
        )

        if video.score >= 80:
            classificacao = "Excelente"
        elif video.score >= 60:
            classificacao = "Bom"
        elif video.score >= 40:
            classificacao = "Médio"
        else:
            classificacao = "Baixo"

        print(
            f"Classificação: {classificacao}"
        )

    report_texto = Report().gerar(videos)

    if not EMAIL_REMETENTE or not EMAIL_SENHA or not EMAIL_DESTINATARIO:
        print(
            "\nE-mail não configurado. "
            "O relatório foi gerado somente no terminal."
        )
        return

    try:

        enviar_relatorio(
            remetente=EMAIL_REMETENTE,
            senha=EMAIL_SENHA,
            destinatario=EMAIL_DESTINATARIO,
            assunto="Teste - Relatório dos vídeos do YouTube",
            conteudo=report_texto,
            servidor=EMAIL_SMTP_SERVIDOR,
            porta=int(EMAIL_SMTP_PORTA)
        )

        print("\nRelatório de teste enviado por e-mail.")

    except Exception as error:

        print(
            f"\nErro ao enviar o relatório de teste: "
            f"{error}"
        )


if __name__ == "__main__":

    main()
