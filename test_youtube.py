import re
import unittest

from models.video import Video
from processor.youtube_score import calcular_scores
from reports.report import Report


def criar_video(video_id, visualizacoes, curtidas, comentarios):
    return Video(
        id=video_id,
        titulo=f"Vídeo {video_id}",
        descricao="Descrição de teste",
        url=f"https://youtube.com/watch?v={video_id}",
        data_publicacao="2026-09-01T00:00:00Z",
        thumbnail="",
        duracao="PT1M",
        visualizacoes=visualizacoes,
        curtidas=curtidas,
        comentarios=comentarios,
    )


def selecionar_novos_videos(videos_atuais, videos_novos):
    ids_atuais = {video.id for video in videos_atuais}
    return [video for video in videos_novos if video.id not in ids_atuais]


def duracao_em_segundos(duracao):
    partes = re.fullmatch(
        r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",
        duracao or "",
    )
    if not partes:
        return 0
    horas, minutos, segundos = (int(valor or 0) for valor in partes.groups())
    return (horas * 3600) + (minutos * 60) + segundos


def eh_short(video):
    return duracao_em_segundos(video.duracao) <= 60


class TestYouTubeScore(unittest.TestCase):
    def test_calcula_score_e_prioriza_video_com_maior_engajamento(self):
        videos = [
            criar_video("melhor", 1000, 100, 20),
            criar_video("menor", 500, 10, 1),
        ]

        calcular_scores(videos)

        self.assertEqual(videos[0].score, 100.0)
        self.assertLess(videos[1].score, videos[0].score)

    def test_lista_vazia_nao_falha(self):
        self.assertEqual(calcular_scores([]), [])

    def test_seleciona_apenas_videos_novos(self):
        atuais = [criar_video("existente", 100, 10, 2)]
        novos = [
            criar_video("existente", 100, 10, 2),
            criar_video("inovador", 500, 50, 5),
        ]

        result = selecionar_novos_videos(atuais, novos)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "inovador")

    def test_separa_short_de_video_normal_pela_duracao(self):
        short = criar_video("short", 100, 10, 1)
        short.duracao = "PT59S"
        video_normal = criar_video("normal", 100, 10, 1)
        video_normal.duracao = "PT1M1S"

        self.assertTrue(eh_short(short))
        self.assertFalse(eh_short(video_normal))


class TestReport(unittest.TestCase):
    def test_relatorio_inclui_score_e_classificacao(self):
        video = criar_video("abc", 100, 10, 2)
        video.score = 85.0

        report = Report().gerar_texto([video])

        self.assertIn("Score: 85.0/100", report)
        self.assertIn("Classificação: Excelente", report)


if __name__ == "__main__":
    unittest.main()