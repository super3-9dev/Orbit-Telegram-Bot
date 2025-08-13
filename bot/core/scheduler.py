
from __future__ import annotations
import os, asyncio, time
from typing import List
from datetime import datetime, timezone

from .models import MarketSnapshot, OddsQuote
from .compare import find_opportunities, pct_change
from .dedupe import DedupeCache
from .notify import send_telegram, format_alert

SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
ALERT_DEDUPE_MINUTES = int(os.getenv("ALERT_DEDUPE_MINUTES", "10"))
DEMO = os.getenv("DEMO", "1") == "1"

from ..sites.orbit import fetch_orbit_snapshots
from ..sites.golbet import fetch_golbet724_snapshots

async def run_cycle(dedupe: DedupeCache):
    # Collect snapshots from all sources
    snapshots: List[MarketSnapshot] = []
    # Orbit (LAY)
    snapshots += await fetch_orbit_snapshots()
    # Comparator sites
    # snapshots += await fetch_golbet724_snapshots()
    # Compare and notify
    now = datetime.now(timezone.utc)
    for m, orbit_q, other_q in find_opportunities(snapshots):
        if dedupe.seen_recently(m.match_id, orbit_q.market, orbit_q.selection):
            continue
        diff_abs = other_q.odds - orbit_q.odds
        diff_pct = pct_change(orbit_q.odds, other_q.odds)
        msg = format_alert(
            match_name=m.match_name,
            league=m.league,
            market=orbit_q.market,
            selection=orbit_q.selection,
            orbit_odds=orbit_q.odds,
            other_site=other_q.site,
            other_odds=other_q.odds,
            detected_dt=now,
            kickoff_dt=m.kickoff_utc,
            diff_pct=diff_pct,
            diff_abs=diff_abs
        )
        await send_telegram(msg)
        dedupe.mark(m.match_id, orbit_q.market, orbit_q.selection)

async def scheduler():
    dedupe = DedupeCache(window_seconds=ALERT_DEDUPE_MINUTES * 60)
    while True:
        start = time.time()
        try:
            await run_cycle(dedupe)
        except Exception as e:
            print("[CYCLE ERROR]", e)
        elapsed = time.time() - start
        sleep_s = max(1.0, SCAN_INTERVAL_SECONDS - elapsed)
        await asyncio.sleep(sleep_s)
