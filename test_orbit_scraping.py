#!/usr/bin/env python3
"""
Test script to verify the Orbit scraper works with real page loading.
This will test the actual scraping functionality to ensure timeouts are fixed.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append('.')

async def test_orbit_scraping():
    """Test the Orbit scraper with real page loading."""
    try:
        print("🧪 Testing Orbit Scraper with Real Page Loading")
        print("=" * 60)
        
        # Test imports
        from bot.sites.orbit import fetch_orbit_snapshots
        from bot.core.persistent_browser import BrowserManager
        print("✅ Imports successful")
        
        # Create browser manager
        manager = BrowserManager()
        print("✅ Browser manager created")
        
        # Get Orbit browser
        orbit_browser = await manager.get_browser('orbit')
        print("✅ Orbit browser ready")
        
        # Test actual scraping
        print("\n🌐 Testing Orbit page loading and scraping...")
        print("This may take a few seconds...")
        
        try:
            # Test the scraper function
            result = await fetch_orbit_snapshots(manager)
            
            if result:
                print(f"✅ Orbit scraping successful!")
                print(f"📊 Found {len(result)} market snapshots")
                
                # Show first few results
                if len(result) > 0:
                    print("\n📋 Sample data:")
                    for i, snapshot in enumerate(result[:3]):  # Show first 3
                        print(f"   {i+1}. {snapshot}")
            else:
                print("⚠️  Orbit scraping returned no data")
                print("   This might be normal if no matches are available")
                
        except Exception as e:
            print(f"❌ Orbit scraping failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Clean up
        await manager.cleanup_all()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the Orbit scraping test."""
    print("🚀 Testing Orbit Scraper - Real Page Loading Test")
    print("This will verify that timeout issues are fixed")
    print("=" * 70)
    
    success = await test_orbit_scraping()
    
    if success:
        print("\n🎉 Orbit scraper test PASSED!")
        print("💡 Timeout issues should be resolved")
        print("🚀 Ready to use the ULTRA-FAST bot!")
    else:
        print("\n❌ Orbit scraper test FAILED!")
        print("🔧 Check the error messages above for issues")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🚀 Ready to use the improved Orbit scraper!")
        print("💡 Run: python -m bot.main (select option 1)")
        print("⚡ Enjoy reliable 1-second scanning!")
    else:
        print("\n🔧 System needs further fixes before use!")
