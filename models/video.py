from dataclasses import dataclass

# Representa um vídeo do YouTube dentro do projeto.
# Essa classe guarda todos os dados necessários para análise e relatório.


@dataclass
class Video:
    """Estrutura dos dados de um vídeo: métricas, URL, título e score final."""

    id: str
    titulo: str
    descricao: str
    url: str
    data_publicacao: str
    thumbnail: str
    duracao: str
    visualizacoes: int
    curtidas: int
    comentarios: int
    score: float = 0.0