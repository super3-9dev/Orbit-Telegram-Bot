from __future__ import annotations
import os, asyncio, time
from datetime import datetime

from .dedupe import DedupeCache
from .notify import send_telegram, format_arbitrage_results, broadcast_to_users
from .team_matcher import find_arbitrage_opportunities
from .user_manager import UserManager
from .persistent_browser import BrowserManager

# Configuration - ULTRA-FAST MODE
SCAN_INTERVAL_SECONDS = float(os.getenv("SCAN_INTERVAL_SECONDS", "1.0"))  # Default to 1 second for ULTRA-FAST scanning
ALERT_DEDUPE_MINUTES = int(os.getenv("ALERT_DEDUPE_MINUTES", "1"))  # Reduced dedupe time for speed

# Import scrapers at function level to avoid circular imports


async def run_cycle(dedupe: DedupeCache, user_manager: UserManager, telegram_bot=None, browser_manager: BrowserManager = None):
    """
    Run one cycle of arbitrage detection with fast scanning.
    
    Args:
        dedupe: DedupeCache instance for preventing duplicate alerts
        user_manager: UserManager instance for user management
        telegram_bot: Optional TelegramBot instance for sending results
        browser_manager: BrowserManager instance for persistent browsers
    """
    try:
        print(f"[SCHEDULER] Starting new cycle (Interval: {SCAN_INTERVAL_SECONDS}s)...")
        registered_users = user_manager.get_registered_users()
        user_count = len(registered_users)
        if user_count == 0:
            print("[SCHEDULER] No registered users, skipping cycle")
            return
        
        print(f"[SCHEDULER] {user_count} registered users, proceeding with cycle")
        
        # Fetch data from both sites using persistent browsers
        print("[SCHEDULER] Fetching data from Orbit...")
        from ..sites.orbit import fetch_orbit_snapshots
        orbitData = await fetch_orbit_snapshots(browser_manager)
        print(f"[SCHEDULER] Orbit data: {len(orbitData)} matches")
        
        print("[SCHEDULER] Fetching data from Golbet...")
        from ..sites.golbet import fetch_golbet724_snapshots
        golbetData = await fetch_golbet724_snapshots(browser_manager)
        print(f"[SCHEDULER] Golbet data: {len(golbetData)} matches")
        
        # Check if we have sufficient data
        if len(orbitData) == 0 or len(golbetData) == 0:
            error_msg = f"""⚠️ <b>DATA COLLECTION ISSUE</b> ⚠️

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> {len(registered_users)} registered users

🚨 <b>Issue Detected:</b>
   • Insufficient data received from betting sites
   • Orbit data: {len(orbitData)} matches
   • Golbet data: {len(golbetData)} matches

🔍 <b>Possible Causes:</b>
   • Website structure changes
   • Network connectivity issues
   • Site maintenance or downtime
   • Scraper configuration issues

💡 <b>What Happens Next:</b>
   • Bot will retry in next cycle ({SCAN_INTERVAL_SECONDS} seconds)
   • Continuous monitoring remains active
   • Alerts will resume when data is available

🛠️ <b>Technical Status:</b>
   • Scraper health: Needs attention
   • Data pipeline: Interrupted
   • Monitoring: Active and alerting

🎯 <b>Stay tuned - normal operations will resume shortly!</b> 🔄"""
            
            if telegram_bot:
                await telegram_bot.broadcast_to_users(error_msg)
            else:
                await broadcast_to_users(error_msg, registered_users)
            return
        
        # Compare data using Python-based matching (no OpenAI)
        print("[SCHEDULER] Comparing data using Python team matching...")
        result = find_arbitrage_opportunities(orbitData, golbetData)
        
        if result:
            print(f"[SCHEDULER] Arbitrage opportunities found: {len(result)}")
            
            try:
                # Format the opportunities result
                msg = format_arbitrage_results(result, orbitData, golbetData)
                
                # Send to users via Telegram bot if available, otherwise use direct broadcast
                if telegram_bot:
                    await telegram_bot.send_arbitrage_results(msg)
                else:
                    await broadcast_to_users(msg, registered_users)
                
                # Update user activity
                for user_id in registered_users:
                    user_manager.update_user_activity(user_id)
                    
            except Exception as e:
                print(f"[SCHEDULER] Error formatting opportunities result: {e}")
                # Fallback: send raw result
                fallback_msg = f"🎯 <b>ARBITRAGE OPPORTUNITIES FOUND!</b> 🎯\n\n{result}"
                if telegram_bot:
                    await telegram_bot.send_arbitrage_results(fallback_msg)
                else:
                    await broadcast_to_users(fallback_msg, registered_users)
        else:
            print("[SCHEDULER] No arbitrage opportunities found")
            no_opportunities_msg = f"""🔍 <b>ARBITRAGE SCAN COMPLETED</b> 🔍

⏰ <b>Scan Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> {len(registered_users)} registered users

📊 <b>Scan Results:</b>
   • ✅ <b>Data Collection:</b> Successful
   • ✅ <b>Team Matching:</b> Completed
   • ❌ <b>Opportunities Found:</b> None

🎯 <b>Threshold Filtering:</b>
   • <b>Range:</b> -1% to +30%
   • <b>Status:</b> Applied successfully
   • <b>Result:</b> No opportunities met criteria

💡 <b>What This Means:</b>
   • Market conditions are currently unfavorable
   • Odds are too close or outside profitable range
   • This is normal - opportunities come and go
   • Stay patient and keep monitoring

🔄 <b>Next Actions:</b>
   • <b>Next Scan:</b> In {SCAN_INTERVAL_SECONDS} seconds
   • <b>Continuous Monitoring:</b> Active
   • <b>Real-time Alerts:</b> Ready

🌟 <b>Stay Optimistic!</b>
   • Opportunities will appear when market conditions change
   • The bot is working correctly and protecting you from bad bets
   • Quality over quantity - we only want profitable opportunities

🎯 <b>Keep monitoring - your next big opportunity is coming!</b> 💰🚀"""
            
            if telegram_bot:
                await telegram_bot.send_no_opportunities_message()
            else:
                await broadcast_to_users(no_opportunities_msg, registered_users)
        
        print("[SCHEDULER] Cycle completed successfully")
        
    except Exception as e:
        print(f"[SCHEDULER] Error in cycle: {e}")
        error_msg = f"""🚨 <b>SCHEDULER ERROR</b> 🚨

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> {len(registered_users)} registered users

❌ <b>Error Details:</b>
   • <b>Type:</b> Cycle execution error
   • <b>Message:</b> {str(e)}
   • <b>Status:</b> Investigation required

🔍 <b>What Happened:</b>
   • An unexpected error occurred during the cycle
   • Data processing was interrupted
   • Error details have been logged for analysis

💡 <b>What Happens Next:</b>
   • Bot will attempt to continue in next cycle
   • Error has been logged for technical review
   • Monitoring remains active despite this issue

🛠️ <b>Technical Response:</b>
   • Error logged with timestamp
   • System will attempt recovery
   • Next cycle scheduled normally

🎯 <b>Don't worry - the bot is designed to handle errors gracefully!</b> 🔄"""
        
        if telegram_bot:
            await telegram_bot.broadcast_to_users(error_msg)
        else:
            registered_users = user_manager.get_registered_users()
            if registered_users:
                await broadcast_to_users(error_msg, registered_users)


async def scheduler(telegram_bot=None):
    """
    Main scheduler function that runs fast arbitrage detection cycles.
    
    Args:
        telegram_bot: Optional TelegramBot instance for sending results
    """
    print(f"[SCHEDULER] Starting FAST arbitrage detection scheduler...")
    print(f"[SCHEDULER] Scan interval: {SCAN_INTERVAL_SECONDS} seconds")
    
    # Initialize components
    dedupe = DedupeCache()
    user_manager = UserManager()
    browser_manager = BrowserManager()
    
    print(f"[SCHEDULER] Initialized with {user_manager.get_user_count()} registered users")
    print("[SCHEDULER] Starting persistent browsers...")
    
    try:
        # Start browsers for both sites
        print("[SCHEDULER] Starting persistent browsers...")
        
        # Start browsers in parallel for faster initialization
        orbit_browser, golbet_browser = await asyncio.gather(
            browser_manager.get_browser('orbit'),
            browser_manager.get_browser('golbet'),
            return_exceptions=True
        )
        
        # Check for exceptions
        if isinstance(orbit_browser, Exception):
            print(f"[SCHEDULER] ❌ Orbit browser failed: {orbit_browser}")
            orbit_browser = None
        if isinstance(golbet_browser, Exception):
            print(f"[SCHEDULER] ❌ Golbet browser failed: {golbet_browser}")
            golbet_browser = None
        
        if not orbit_browser or not golbet_browser:
            print("[SCHEDULER] ❌ Failed to start persistent browsers")
            raise Exception("Persistent browser initialization failed")
            
        print("[SCHEDULER] ✅ Persistent browsers started successfully")
        
        while True:
            # Run one cycle
            await run_cycle(dedupe, user_manager, telegram_bot, browser_manager)
            
            # Sleep for the configured interval (much faster now)
            print(f"[SCHEDULER] Cycle completed, sleeping for {SCAN_INTERVAL_SECONDS:.2f}s")
            await asyncio.sleep(SCAN_INTERVAL_SECONDS)
            
    except Exception as e:
        print(f"[SCHEDULER] Top-level error: {e}")
        # Try to notify users about the error
        if telegram_bot:
            await telegram_bot.broadcast_to_users(f"""🚨 <b>CRITICAL SCHEDULER ERROR</b> 🚨

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> All registered users

❌ <b>Critical Issue:</b>
   • <b>Type:</b> Scheduler crash
   • <b>Message:</b> {str(e)}
   • <b>Status:</b> System restart required

🚨 <b>What Happened:</b>
   • A critical error caused the scheduler to crash
   • Arbitrage detection has stopped
   • Immediate attention is required

💡 <b>What Happens Next:</b>
   • Bot will attempt to restart automatically
   • All systems will be reinitialized
   • Monitoring will resume after restart

🛠️ <b>Technical Response:</b>
   • Error logged with full details
   • Automatic restart initiated
   • Recovery procedures activated

🎯 <b>Stay calm - the bot is designed to recover automatically!</b> 🔄

⚠️ <b>Note:</b> This is a rare occurrence. The bot will be back online shortly.""")
        else:
            registered_users = user_manager.get_registered_users()
            if registered_users:
                await broadcast_to_users(f"""🚨 <b>CRITICAL SCHEDULER ERROR</b> 🚨

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👥 <b>Recipients:</b> All registered users

❌ <b>Critical Issue:</b>
   • <b>Type:</b> Scheduler crash
   • <b>Message:</b> {str(e)}
   • <b>Status:</b> System restart required

🚨 <b>What Happened:</b>
   • A critical error caused the scheduler to crash
   • Arbitrage detection has stopped
   • Immediate attention is required

💡 <b>What Happens Next:</b>
   • Bot will attempt to restart automatically
   • All systems will be reinitialized
   • Monitoring will resume after restart

🛠️ <b>Technical Response:</b>
   • Error logged with full details
   • Automatic restart initiated
   • Recovery procedures activated

🎯 <b>Stay calm - the bot is designed to recover automatically!</b> 🔄

⚠️ <b>Note:</b> This is a rare occurrence. The bot will be back online shortly.""", registered_users)
        
        # Wait before potentially restarting
        await asyncio.sleep(10)
    
    finally:
        # Clean up browsers
        print("[SCHEDULER] Cleaning up persistent browsers...")
        await browser_manager.cleanup_all()
