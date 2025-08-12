
from __future__ import annotations
import os
import httpx
from datetime import datetime
import pytz

# Read TZ at import; read token/chat at send-time to avoid empty values from early import
TZ = os.getenv("TZ", "Asia/Tokyo")

def ts(dt) -> str:
    try:
        tz = pytz.timezone(TZ)
        return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

async def send_telegram(text: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        print("[TELEGRAM DISABLED]", text)
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={
            "chat_id": chat_id,
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
