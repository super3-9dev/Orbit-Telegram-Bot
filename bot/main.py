
from __future__ import annotations
import asyncio, os
from dotenv import load_dotenv
from .core.scheduler import scheduler

def main():
    load_dotenv()
    print("[BOT] Starting Orbit Lay-Odds Arbitrage Bot...")
    print(f"[BOT] DEMO={'1' if os.getenv('DEMO','1')=='1' else '0'}  interval={os.getenv('SCAN_INTERVAL_SECONDS','60')}s")
    asyncio.run(scheduler())

if __name__ == "__main__" or __name__ == "bot.main":
    main()
