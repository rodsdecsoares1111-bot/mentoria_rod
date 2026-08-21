from dataclasses import dataclass

@dataclass
class Video:

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
