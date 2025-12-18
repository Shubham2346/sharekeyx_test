from pydantic import BaseModel
from typing import Optional

class MarketTick(BaseModel):
    symbol: str
    ltp: float
    volume: Optional[int]
    timestamp: int
