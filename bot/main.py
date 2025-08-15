
from __future__ import annotations
import asyncio, os, sys
from dotenv import load_dotenv

def print_banner():
    """Print a beautiful banner for the application."""
    print("""
🤖 ╔══════════════════════════════════════════════════════════════╗ 🤖
   ║                    ORBIT ARBITRAGE BOT                        ║
   ║                    FAST SCANNING SYSTEM                       ║
   ╚══════════════════════════════════════════════════════════════╝
   
🚀 Welcome to the Ultra-Fast Arbitrage Detection System!
📱 Now with Telegram Bot Integration and Persistent Browsers
    💰 Real-time arbitrage opportunities every 1 second
⚡ No OpenAI dependency - Pure Python team matching
""")

def print_menu():
    """Print the main menu options."""
    print("""
📋 **AVAILABLE MODES:**

1️⃣  ULTRA-FAST ARBITRAGE BOT MODE
    • Run the ULTRA-FAST arbitrage detection system
    • Scan every 1 second (ULTRA-FAST MODE)
    • Persistent browsers for maximum speed
    • Python-based team matching (no API costs)
    • Send notifications to all registered users

2️⃣  TELEGRAM BOT MODE  
    • Handle user registration and commands
    • Process /start, /stop, /help commands
    • Manage user subscriptions
    • No arbitrage detection (bot only)

3️⃣  BOTH MODES (RECOMMENDED)
    • Run both systems simultaneously
    • Full functionality with user management
    • Fast scanning + Telegram integration
    • Best for production use

4️⃣  CONFIGURE SCANNING SPEED
    • Set custom scan intervals
    • Adjust browser settings
    • Configure team matching thresholds

0️⃣  EXIT
    • Close the application

""")

async def run_arbitrage_bot():
    """Run the fast arbitrage detection bot."""
    print("🚀 Starting ULTRA-FAST Arbitrage Bot...")
    print("⚡ Scan interval: 1 second (ULTRA-FAST MODE)")
    print("🌐 Persistent browsers: Enabled")
    print("🤖 Team matching: Python-based (no OpenAI)")
    print("🚀 ULTRA-FAST MODE: Maximum performance enabled!")
    
    try:
        from .core.scheduler import scheduler
        await scheduler()
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        import traceback
        traceback.print_exc()

async def run_telegram_bot():
    """Run the Telegram bot for user management."""
    print("📱 Starting Telegram Bot...")
    from .telegram_bot import TelegramBot
    bot = TelegramBot()
    await bot.run()

async def run_both_modes():
    """Run both the fast arbitrage bot and Telegram bot simultaneously."""
    try:
        print("🚀📱 Starting both modes...")
        print("⚡ Fast scanning + Telegram integration")
        
        # Initialize Telegram bot first
        from .telegram_bot import TelegramBot
        telegram_bot = TelegramBot()
        
        # Start both tasks with the Telegram bot instance
        await asyncio.gather(
            run_arbitrage_bot(),  # Use the function instead of direct import
            telegram_bot.run()
        )
        
    except Exception as e:
        print(f"❌ Error in both modes: {e}")
        import traceback
        traceback.print_exc()

async def configure_scanning():
    """Configure scanning speed and settings."""
    print("⚙️  Scanning Configuration")
    print("=" * 50)
    
    current_interval = os.getenv("SCAN_INTERVAL_SECONDS", "1.0")
    print(f"Current scan interval: {current_interval} seconds")
    
    print("\n📊 Available scan intervals:")
    print("   • 1 second - ULTRA-FAST (default)")
    print("   • 0.5 seconds - EXTREME SPEED")
    print("   • 2 seconds - Fast")
    print("   • 5 seconds - Moderate")
    print("   • 10 seconds - Conservative")
    
    try:
        new_interval = input("\n🎯 Enter new scan interval in seconds (or press Enter to keep current): ").strip()
        
        if new_interval:
            # Validate input
            try:
                interval = float(new_interval)
                if interval < 0.5:
                    print("❌ Interval too fast (minimum 0.5 seconds)")
                    return
                elif interval > 300:
                    print("❌ Interval too slow (maximum 300 seconds)")
                    return
                
                # Update environment variable
                os.environ["SCAN_INTERVAL_SECONDS"] = str(interval)
                print(f"✅ Scan interval updated to {interval} seconds")
                print("💡 Restart the bot for changes to take effect")
                
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
        else:
            print("ℹ️  Keeping current scan interval")
            
    except KeyboardInterrupt:
        print("\n⏹️  Configuration cancelled")

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables (removed OpenAI requirement)
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Please create a .env file with the required variables.")
        print("   See README.md for setup instructions.")
        sys.exit(1)
    
    # Print banner
    print_banner()
    
    while True:
        try:
            print_menu()
            choice = input("🎯 Select mode (0-4): ").strip()
            
            if choice == "0":
                print("👋 Goodbye! Thanks for using Fast Arbitrage Bot!")
                break
                
            elif choice == "1":
                print("🚀 Starting Fast Arbitrage Bot Mode...")
                asyncio.run(run_arbitrage_bot())
                
            elif choice == "2":
                print("📱 Starting Telegram Bot Mode...")
                asyncio.run(run_telegram_bot())
                
            elif choice == "3":
                print("🚀📱 Starting Both Modes...")
                asyncio.run(run_both_modes())
                
            elif choice == "4":
                print("⚙️  Opening Configuration...")
                asyncio.run(configure_scanning())
                
            else:
                print("❌ Invalid choice. Please select 0, 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Restarting main menu...")
            continue

if __name__ == "__main__" or __name__ == "bot.main":
    main()
