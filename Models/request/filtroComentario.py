from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FiltroSentences(BaseModel):
    fechaIni: Optional[datetime] = None
    fechaFin: Optional[datetime] = None
    temasId: List[int] = []
    listId: List[str] = []  
    min_info : Optional[bool] = False
    
class InfoGrafGeneral(BaseModel):
    graf_word_cloud: Optional[List[dict]] = None