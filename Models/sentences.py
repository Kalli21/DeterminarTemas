from pydantic import BaseModel
from typing import List
from datetime import datetime

class Sentence(BaseModel):
    id: str = ''
    text: str
    temas: dict = {} 
    fecha: datetime