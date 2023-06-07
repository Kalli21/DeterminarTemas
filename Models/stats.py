from pydantic import BaseModel

class StatsUser(BaseModel):
    total: int = 0