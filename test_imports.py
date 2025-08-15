#!/usr/bin/env python3
"""
Simple import test for the new system.
"""

def test_imports():
    """Test all imports."""
    try:
        print("🔍 Testing imports...")
        
        # Test team matcher
        from bot.core.team_matcher import TeamMatcher, ArbitrageCalculator, find_arbitrage_opportunities
        print("✅ Team matcher imports successful")
        
        # Test persistent browser
        from bot.core.persistent_browser import PersistentBrowser, BrowserManager
        print("✅ Persistent browser imports successful")
        
        # Test notify
        from bot.core.notify import format_arbitrage_results, send_telegram, broadcast_to_users
        print("✅ Notify imports successful")
        
        # Test scheduler
        from bot.core.scheduler import run_cycle, scheduler
        print("✅ Scheduler imports successful")
        
        # Test user manager
        from bot.core.user_manager import UserManager
        print("✅ User manager imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    
    if success:
        print("\n🚀 System is ready!")
        print("💡 You can now run: python -m bot.main")
    else:
        print("\n🔧 System needs fixes!")
