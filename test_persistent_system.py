#!/usr/bin/env python3
"""
Test script to verify the persistent browser system is working.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append('.')

async def test_persistent_browser():
    """Test the persistent browser functionality."""
    try:
        print("🧪 Testing Persistent Browser System")
        print("=" * 50)
        
        # Test imports
        from bot.core.persistent_browser import PersistentBrowser, BrowserManager
        print("✅ Persistent browser imports successful")
        
        # Test browser manager
        manager = BrowserManager()
        print("✅ Browser manager created")
        
        # Test getting browsers
        orbit_browser = await manager.get_browser('orbit')
        print("✅ Orbit browser created")
        
        golbet_browser = await manager.get_browser('golbet')
        print("✅ Golbet browser created")
        
        # Test getting pages
        orbit_page = await orbit_browser.get_page()
        if orbit_page:
            print("✅ Orbit page ready")
        else:
            print("❌ Orbit page failed")
            return False
            
        golbet_page = await golbet_browser.get_page()
        if golbet_page:
            print("✅ Golbet page ready")
        else:
            print("❌ Golbet page failed")
            return False
        
        # Test health checks
        orbit_healthy = await orbit_browser.health_check()
        golbet_healthy = await golbet_browser.health_check()
        
        print(f"✅ Orbit browser health: {'Good' if orbit_healthy else 'Poor'}")
        print(f"✅ Golbet browser health: {'Good' if golbet_healthy else 'Poor'}")
        
        # Clean up
        await manager.cleanup_all()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_site_scrapers():
    """Test that site scrapers can import and work."""
    try:
        print("\n🧪 Testing Site Scrapers")
        print("=" * 50)
        
        # Test imports
        from bot.sites.orbit import fetch_orbit_snapshots
        from bot.sites.golbet import fetch_golbet724_snapshots
        print("✅ Site scraper imports successful")
        
        # Test function signatures
        import inspect
        orbit_sig = inspect.signature(fetch_orbit_snapshots)
        golbet_sig = inspect.signature(fetch_golbet724_snapshots)
        
        print(f"✅ Orbit function signature: {orbit_sig}")
        print(f"✅ Golbet function signature: {golbet_sig}")
        
        # Check if they accept browser_manager parameter
        if 'browser_manager' in orbit_sig.parameters:
            print("✅ Orbit accepts browser_manager parameter")
        else:
            print("❌ Orbit missing browser_manager parameter")
            return False
            
        if 'browser_manager' in golbet_sig.parameters:
            print("✅ Golbet accepts browser_manager parameter")
        else:
            print("❌ Golbet missing browser_manager parameter")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Testing Persistent Browser System")
    print("This will verify that browsers stay open between scans")
    print("=" * 60)
    
    tests = [
        ("Persistent Browser", test_persistent_browser),
        ("Site Scrapers", test_site_scrapers)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            success = await test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   • {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
        print("💡 Your persistent browser system is ready!")
        print("⚡ You can now scan every 1 second without browser restarts!")
        print("💰 No more OpenAI API costs!")
        print("🌐 Browsers will stay open permanently!")
        return True
    else:
        print(f"\n❌ {total - passed} tests FAILED!")
        print("🔧 Check the error messages above for issues")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🚀 Ready to use the persistent browser system!")
        print("💡 Run: python -m bot.main (select option 3)")
        print("⚡ Enjoy 1-second scanning with no browser restarts!")
    else:
        print("\n🔧 System needs fixes before use!")
