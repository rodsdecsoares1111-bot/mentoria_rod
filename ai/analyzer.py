from openai import OpenAI

from config import OPENAI_API_KEY

class AIAnalyzer:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    def analisar_video(self, video):

        prompt = f"""
Analise o seguinte vídeo do YouTube.

Título:
{video.titulo}

Descrição:
{video.descricao}

Visualizações:
{video.visualizacoes}

Curtidas:
{video.curtidas}

Comentários:
{video.comentarios}

Forneça:

1. Resumo do conteúdo provável
2. Tema principal
3. Público-alvo
4. Avaliação do engajamento
5. Sugestão para melhorar o conteúdo
"""

        response = (
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        return response.choices[0].message.content
