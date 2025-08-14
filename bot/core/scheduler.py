from __future__ import annotations
import os, asyncio, time
from typing import List
from datetime import datetime, timezone

from .models import MarketSnapshot
from .compare import find_opportunities, pct_change
from .dedupe import DedupeCache
from .notify import send_telegram, format_alert, format_ai_analysis_result
from .openai import compare

SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
ALERT_DEDUPE_MINUTES = int(os.getenv("ALERT_DEDUPE_MINUTES", "10"))

from ..sites.orbit import fetch_orbit_snapshots
from ..sites.golbet import fetch_golbet724_snapshots


async def run_cycle(dedupe: DedupeCache):
    orbitData = await fetch_orbit_snapshots()
    golbetData = await fetch_golbet724_snapshots()
    # Compare and notify
    result = compare(orbitData, golbetData)
    
    if result:
        try:
            # Format and send the result via Telegram
            msg = format_ai_analysis_result(result, orbitData, golbetData)
            await send_telegram(msg)
            
        except Exception as e:
            print(f"Error processing AI result: {e}")
            # Send raw result if formatting fails
            await send_telegram(f"🤖 AI Analysis Result:\n\n{result}")
    else:
        print("No comparison result received")
        await send_telegram("❌ No arbitrage opportunities found in this cycle")


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
