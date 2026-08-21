from pyairtable import Api

from config import (
    AIRTABLE_TOKEN,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_NAME
)

class AirtableDatabase:

    def __init__(self):

        api = Api(
            AIRTABLE_TOKEN
        )

        self.table = api.table(
            AIRTABLE_BASE_ID,
            AIRTABLE_TABLE_NAME
        )

    def salvar_video(self, video):

        # Extrair apenas a data (YYYY-MM-DD)
        data_formatada = (
            video.data_publicacao.split("T")[0]
            if video.data_publicacao 
            else ""
        )

        dados = {

            "ID": video.id,

            "Título": video.titulo,

            "Descrição": video.descricao,

            "URL": video.url,

            "Data": data_formatada,

            "Thumbnail": video.thumbnail,

            "Visualizações": video.visualizacoes,

            "Curtidas": video.curtidas,

            "Comentários": video.comentarios

        }

        self.table.create(dados)
