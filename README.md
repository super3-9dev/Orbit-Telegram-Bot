
# Orbit Lay-Odds Arbitrage Bot (Base Project)

Minimal, production-lean skeleton for a **Telegram-first** football odds arbitrage bot.
This base matches your client's requirements: fetch **Orbit LAY odds** (pink boxes), compare with other sites, 
and send **real-time Telegram alerts** when **Orbit_LAY ≤ Other_ODDS** for the same market/selection.

> This is a **starter**: Orbit/comparator scrapers are stubbed for safety. Replace with real fetchers in `bot/sites/`.

---

## Quick Start

1) **Python 3.11+** recommended.

2) Create a virtual env and install deps:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) Copy `.env.example` to `.env` and fill your values:
```bash
cp .env.example .env
```

4) **Run (demo mode):**
```bash
python -m bot.main
```
Demo mode simulates data and prints or sends Telegram messages (if token/chat set).

---

## Environment (.env)

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

ORBIT_USERNAME=
ORBIT_PASSWORD=
ORBIT_BASE_URL=https://example-orbit.com

COMPARATOR_SITES=example_site
SCAN_INTERVAL_SECONDS=60
ALERT_DEDUPE_MINUTES=10
MIN_DIFF_ABS=0.00
MIN_DIFF_PCT=0.0
TZ=Asia/Tokyo
DEMO=1
USE_PROXY=false
HTTP_PROXY=
```

- Set `DEMO=0` to run real fetchers (after you implement endpoints in `bot/sites/`).
- `TZ` controls how times are presented in alerts (default Asia/Tokyo).

---

## Project Layout

```
/bot
  /core
    compare.py       # trigger logic Orbit_LAY ≤ Other
    dedupe.py        # simple de-duplication per match/market/selection
    matchers.py      # name/market normalization helpers
    models.py        # Pydantic models
    notify.py        # Telegram notifier
    scheduler.py     # 60s async loop
  /sites
    orbit.py         # Orbit fetcher (stubbed)
    example.py       # Comparator site fetcher (stubbed)
  main.py            # wires everything
.env.example
requirements.txt
```

---

## Implementing Real Fetchers

- **Prefer XHR/JSON endpoints** if available.
- Use `httpx.AsyncClient` with session cookies, headers, and retry (see `tenacity` or custom backoff).
- Make each fetcher return a list of `MarketSnapshot` objects (see `bot/core/models.py`).

**Orbit**: fetch **LAY** odds only (pink boxes).  
**Others**: fetch odds for the **same markets** so comparisons are valid.

---

## Alert Format (Telegram)

```
ARBITRAGE SIGNAL (Orbit LAY ≤ Other)
Match: Team A vs Team B (League)
Market: 1X2 — Draw
Orbit LAY: 3.50
Other: 3.60 (example_site)
Diff: -0.10 (-2.78%)
Detected: 2025-08-12 11:32:05 JST
Kickoff: 2025-08-12 21:00 JST
```

---

## Notes

- This repo avoids site-specific code in public. Insert your real parsing in `bot/sites/`.
- Add proxies/stealth if target sites are strict.
- For production: consider systemd, Docker, or PM2 equivalent to keep the process running.
