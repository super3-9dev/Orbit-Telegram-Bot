#!/usr/bin/env python3
"""
Simple test to check imports and identify errors.
"""

def test_basic_imports():
    """Test basic imports."""
    try:
        print("Testing basic imports...")
        
        # Test core modules
        from bot.core.persistent_browser import BrowserManager
        print("✅ Persistent browser import successful")
        
        from bot.core.scheduler import scheduler
        print("✅ Scheduler import successful")
        
        from bot.core.team_matcher import find_arbitrage_opportunities
        print("✅ Team matcher import successful")
        
        print("✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scraper_imports():
    """Test scraper imports."""
    try:
        print("\nTesting scraper imports...")
        
        # Test scraper modules
        from bot.sites.orbit import fetch_orbit_snapshots
        print("✅ Orbit scraper import successful")
        
        from bot.sites.golbet import fetch_golbet724_snapshots
        print("✅ Golbet scraper import successful")
        
        print("✅ All scraper imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Scraper import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Imports for Orbit Bot")
    print("=" * 40)
    
    test1 = test_basic_imports()
    test2 = test_scraper_imports()
    
    if test1 and test2:
        print("\n🎉 All imports successful! Bot should work.")
    else:
        print("\n❌ Some imports failed. Bot won't start.")
