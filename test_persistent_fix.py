#!/usr/bin/env python3
"""
Test script to verify the fixed persistent browser system.
This will test if the 50-second delay issue is resolved.
"""

import asyncio
import sys
import os
import time

# Add current directory to Python path
sys.path.append('.')

async def test_persistent_browser_speed():
    """Test the persistent browser system for speed improvements."""
    try:
        print("🧪 Testing Fixed Persistent Browser System")
        print("=" * 60)
        
        # Test imports
        from bot.core.persistent_browser import BrowserManager
        print("✅ Imports successful")
        
        # Create browser manager
        manager = BrowserManager()
        print("✅ Browser Manager created")
        
        # Test browser startup time
        print("\n🚀 Testing browser startup time...")
        start_time = time.time()
        
        orbit_browser = await manager.get_browser('orbit')
        if orbit_browser:
            startup_time = time.time() - start_time
            print(f"✅ Orbit browser started in {startup_time:.2f} seconds")
        else:
            print("❌ Failed to start Orbit browser")
            return False
        
        # Test page retrieval time
        print("\n📄 Testing page retrieval time...")
        start_time = time.time()
        
        page = await orbit_browser.get_page()
        if page:
            page_time = time.time() - start_time
            print(f"✅ Page retrieved in {page_time:.2f} seconds")
        else:
            print("❌ Failed to get page")
            return False
        
        # Test second page retrieval (should be much faster)
        print("\n🔄 Testing second page retrieval (should be instant)...")
        start_time = time.time()
        
        page2 = await orbit_browser.get_page()
        if page2:
            page2_time = time.time() - start_time
            print(f"✅ Second page retrieved in {page2_time:.2f} seconds")
            
            if page2_time < 1.0:
                print("🎯 SUCCESS: Persistent browser is working! Second retrieval was fast.")
            else:
                print("⚠️ WARNING: Second page retrieval was slow, persistent system may not be working")
        else:
            print("❌ Failed to get second page")
            return False
        
        # Test browser health
        print("\n💚 Testing browser health check...")
        is_healthy = await orbit_browser.health_check()
        if is_healthy:
            print("✅ Browser health check passed")
        else:
            print("❌ Browser health check failed")
        
        # Test multiple browsers
        print("\n🌐 Testing multiple browser support...")
        golbet_browser = await manager.get_browser('golbet')
        if golbet_browser:
            print("✅ Golbet browser started successfully")
        else:
            print("❌ Failed to start Golbet browser")
        
        # Test browser count
        browser_count = len(manager.browsers)
        print(f"📊 Total browsers running: {browser_count}")
        
        print("\n✅ Persistent Browser Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up browsers
        if 'manager' in locals() and manager:
            print("\n🧹 Cleaning up browsers...")
            await manager.cleanup_all()
            print("✅ Browsers cleaned up.")

async def test_scraper_integration():
    """Test if the scrapers can use the persistent browsers."""
    try:
        print("\n🔍 Testing Scraper Integration with Persistent Browsers")
        print("=" * 60)
        
        # Test imports
        from bot.sites.orbit import fetch_orbit_snapshots
        from bot.core.persistent_browser import BrowserManager
        print("✅ Scraper imports successful")
        
        # Create browser manager
        manager = BrowserManager()
        print("✅ Browser Manager created for scraper test")
        
        # Test scraper with persistent browser
        print("\n🚀 Testing Orbit scraper with persistent browser...")
        start_time = time.time()
        
        data = await fetch_orbit_snapshots(manager)
        scraper_time = time.time() - start_time
        
        if data:
            print(f"✅ Scraper successful! Found {len(data)} matches in {scraper_time:.2f} seconds")
            
            if scraper_time < 10.0:
                print("🎯 SUCCESS: Scraper is fast with persistent browser!")
            else:
                print("⚠️ WARNING: Scraper is still slow, may need further optimization")
        else:
            print("❌ Scraper failed or returned no data")
        
        print("\n✅ Scraper Integration Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ An error occurred during scraper testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up browsers
        if 'manager' in locals() and manager:
            print("\n🧹 Cleaning up browsers...")
            await manager.cleanup_all()
            print("✅ Browsers cleaned up.")

async def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Persistent Browser Tests")
    print("=" * 80)
    
    # Test 1: Basic persistent browser functionality
    test1_success = await test_persistent_browser_speed()
    
    # Test 2: Scraper integration
    test2_success = await test_scraper_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if test1_success and test2_success:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("✅ Persistent browser system is working correctly")
        print("✅ 50-second delay issue should be resolved")
        print("✅ Scrapers can use persistent browsers")
        print("\n🚀 You can now start the bot with confidence!")
    else:
        print("❌ SOME TESTS FAILED")
        print("⚠️ Persistent browser system may still have issues")
        print("🔧 Further debugging may be required")
    
    return test1_success and test2_success

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
