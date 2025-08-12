
from __future__ import annotations
import os
import httpx
from datetime import datetime
import pytz

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TZ = os.getenv("TZ", "Asia/Tokyo")

def ts(dt) -> str:
    try:
        tz = pytz.timezone(TZ)
        return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

async def send_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TELEGRAM DISABLED]", text)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text
        })

def format_alert(match_name: str, league: str|None, market: str, selection: str,
                 orbit_odds: float, other_site: str, other_odds: float,
                 detected_dt, kickoff_dt=None, diff_pct=None, diff_abs=None):
    lines = []
    lines.append("ARBITRAGE SIGNAL (Orbit LAY ≤ Other)")
    lines.append(f"Match: {match_name} ({league})" if league else f"Match: {match_name}")
    lines.append(f"Market: {market} — {selection}")
    lines.append(f"Orbit LAY: {orbit_odds:.2f}")
    lines.append(f"Other: {other_odds:.2f} ({other_site})")
    if diff_abs is not None and diff_pct is not None:
        lines.append(f"Diff: {diff_abs:+.2f} ({diff_pct:+.2f}%)")
    lines.append(f"Detected: {ts(detected_dt)}")
    if kickoff_dt:
        lines.append(f"Kickoff: {ts(kickoff_dt)}")
    return "\n".join(lines)
