import os

from collectors.youtube import (
    YouTubeCollector
)

from collectors.instagram import (
    get_instagram_media
)

from processor.processor import (
    Processor
)

from database.airtable import (
    AirtableDatabase
)

from reports.report import (
    Report
)

from ai.analyzer import (
    AIAnalyzer
)

from notifications.email import (
    enviar_relatorio
)

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
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


def coletar_youtube():

    collector = YouTubeCollector()

    videos = collector.coletar_videos(
        quantidade=10
    )

    print(
        f"\nTotal coletado: "
        f"{len(videos)} vídeos"
    )

    return videos


def coletar_instagram():

    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_USER_ID:
        print(
            "\nInstagram não configurado. "
            "Defina INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_USER_ID no ambiente."
        )
        return []

    instagram_posts = get_instagram_media(
        access_token=INSTAGRAM_ACCESS_TOKEN,
        instagram_user_id=INSTAGRAM_USER_ID
    )

    print(
        f"\nTotal coletado do Instagram: "
        f"{len(instagram_posts)} posts"
    )

    return instagram_posts


def processar_e_salvar_videos(videos):

    processor = Processor()

    videos = processor.processar(
        videos
    )

    database = AirtableDatabase()

    for video in videos:

        try:

            database.salvar_video(
                video
            )

        except Exception as error:

            print(
                f"Erro ao salvar "
                f"{video.titulo}: "
                f"{error}"
            )

    print(
        "\nDados enviados para o Airtable."
    )

    return videos


def gerar_relatorio_e_analise(videos):

    report = Report()

    report_texto = report.gerar(videos)

    analyzer = AIAnalyzer()

    print()
    print("=" * 60)
    print("ANÁLISE DA IA")
    print("=" * 60)

    for video in videos:

        try:

            analise = (
                analyzer.analisar_video(
                    video
                )
            )

            print()
            print("-" * 60)

            print(
                f"Vídeo: "
                f"{video.titulo}"
            )

            print()

            print(analise)

        except Exception as error:

            print(
                f"Erro na análise de "
                f"{video.titulo}: "
                f"{error}"
            )

    return report_texto


def enviar_relatorio_por_email(report_texto):

    if not EMAIL_REMETENTE or not EMAIL_SENHA or not EMAIL_DESTINATARIO:
        print(
            "\nE-mail não configurado. "
            "Defina EMAIL_REMETENTE, EMAIL_SENHA e "
            "EMAIL_DESTINATARIO no ambiente."
        )
        return

    try:

        enviar_relatorio(
            remetente=EMAIL_REMETENTE,
            senha=EMAIL_SENHA,
            destinatario=EMAIL_DESTINATARIO,
            assunto="Relatório dos vídeos do YouTube",
            conteudo=report_texto,
            servidor=EMAIL_SMTP_SERVIDOR,
            porta=int(EMAIL_SMTP_PORTA)
        )

        print("\nRelatório enviado por e-mail.")

    except Exception as error:

        print(
            f"\nErro ao enviar o relatório por e-mail: "
            f"{error}"
        )


def main():

    print()
    print("=" * 60)
    print("MENTORIA")
    print("Monitoramento do YouTube")
    print("=" * 60)
    print()

    # ------------------------------
    # 1. COLETAR
    # ------------------------------

    videos = coletar_youtube()

    # Cada rede permanece em seu próprio formato e fluxo.
    coletar_instagram()

    # ------------------------------
    # 2. PROCESSAR
    # ------------------------------

    videos = processar_e_salvar_videos(videos)

    # ------------------------------
    # 4. RELATÓRIO
    # ------------------------------

    report_texto = gerar_relatorio_e_analise(videos)

    # O envio é opcional e não interrompe as integrações das redes.
    enviar_relatorio_por_email(report_texto)

if __name__ == "__main__":

    main()
