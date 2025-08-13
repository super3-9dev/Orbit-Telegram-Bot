from __future__ import annotations
import os, asyncio, time
from typing import List
from datetime import datetime, timezone

from .models import MarketSnapshot
from .compare import find_opportunities, pct_change
from .dedupe import DedupeCache
from .notify import send_telegram, format_alert

SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
ALERT_DEDUPE_MINUTES = int(os.getenv("ALERT_DEDUPE_MINUTES", "10"))

from ..sites.orbit import fetch_orbit_snapshots
from ..sites.golbet import fetch_golbet724_snapshots


async def run_cycle(dedupe: DedupeCache):
    orbitData = await fetch_orbit_snapshots()
    golbetData = await fetch_golbet724_snapshots()
    # Compare and notify
    for m, orbit_q, other_q in :
        
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
