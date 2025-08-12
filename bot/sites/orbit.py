
from __future__ import annotations
import os, asyncio
from typing import List
from datetime import datetime, timezone, timedelta
from ..core.models import MarketSnapshot, OddsQuote
from ..core.matchers import match_id

DEMO = os.getenv("DEMO", "1") == "1"

async def fetch_orbit_snapshots() -> List[MarketSnapshot]:
    if DEMO:
        # Simulated: Orbit LAY odds for one match
        league = "EPL"
        kickoff = datetime.now(timezone.utc) + timedelta(hours=6)
        mid = match_id(league, kickoff.strftime("%Y-%m-%d"), "Arsenal", "Chelsea")
        m = MarketSnapshot(
            match_id=mid,
            match_name="Arsenal vs Chelsea",
            league=league,
            kickoff_utc=kickoff,
            quotes=[
                OddsQuote(site="orbit", market="1X2", selection="Home", odds=2.10, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Draw", odds=3.50, kind="LAY"),
                OddsQuote(site="orbit", market="1X2", selection="Away", odds=3.40, kind="LAY"),
                OddsQuote(site="orbit", market="OVER_UNDER", selection="Over 2.5", odds=1.95, kind="LAY"),
                OddsQuote(site="orbit", market="OVER_UNDER", selection="Under 2.5", odds=1.90, kind="LAY"),
            ]
        )
        await asyncio.sleep(0.05)
        return [m]
    else:
        # TODO: Implement real Orbit fetcher: login, session, fetch LAY odds only (pink boxes)
        # Return list[MarketSnapshot]
        return []
