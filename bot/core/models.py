
from __future__ import annotations
from typing import Literal, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class OddsQuote(BaseModel):
    site: str
    market: Literal["1X2","OVER_UNDER","CORRECT_SCORE"]
    selection: str            # e.g., 'Home', 'Draw', 'Away' or 'Over 2.5'
    odds: float
    kind: Literal["LAY","BACK"] = "BACK"

class MarketSnapshot(BaseModel):
    match_id: str             # normalized key (league|date|home|away)
    match_name: str           # 'Arsenal vs Chelsea'
    league: Optional[str] = None
    kickoff_utc: Optional[datetime] = None
    quotes: List[OddsQuote] = Field(default_factory=list)
