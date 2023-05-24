from pydantic import BaseModel
from typing import List

class Sentence(BaseModel):
    id: str = ''
    text: str
    temas: dict = {} 