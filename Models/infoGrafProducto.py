from pydantic import BaseModel
from typing import List


class InfoGrafProducto(BaseModel):
    temas: List = []
    comentariosId: List[int] = []