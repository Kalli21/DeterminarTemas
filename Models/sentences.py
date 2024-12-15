from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Sentence(BaseModel):
    id: str = ''
    text: str = ''
    temas: dict = {}
    tema: Optional[int] = -1 
    fecha: Optional[datetime] = None