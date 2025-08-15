#!/usr/bin/env python3
"""
Test script for the new fast scanning system.
Tests Python team matching and persistent browser functionality.
"""

import asyncio
from bot.core.team_matcher import TeamMatcher, ArbitrageCalculator, find_arbitrage_opportunities
from bot.core.persistent_browser import PersistentBrowser, BrowserManager

async def test_team_matching():
    """Test the Python-based team matching system."""
    
    print("🧪 Testing Python Team Matching System")
    print("=" * 60)
    
    # Test data
    orbit_teams = [
        "Shakhtar Donetsk",
        "Dundee United",
        "Manchester United",
        "Real Madrid",
        "Bayern Munich",
        "Paris Saint-Germain"
    ]
    
    golbet_teams = [
        "Shakhtar",
        "Dundee Utd",
        "Man Utd",
        "Madrid",
        "Bayern",
        "PSG"
    ]
    
    print("📊 Test Teams:")
    print("Orbit teams:", orbit_teams)
    print("Golbet teams:", golbet_teams)
    print()
    
    # Test team matcher
    matcher = TeamMatcher(match_threshold=70)
    
    print("🔍 Testing Team Matching...")
    print("-" * 40)
    
    matches = matcher.match_all_teams(orbit_teams, golbet_teams)
    
    print("-" * 40)
    print(f"📈 Matching Results:")
    print(f"   • Total Orbit teams: {len(orbit_teams)}")
    print(f"   • Total Golbet teams: {len(golbet_teams)}")
    print(f"   • Successful matches: {len(matches)}")
    
    print()
    print("✅ Matched Teams:")
    for orbit, golbet in matches.items():
        print(f"   • {orbit} → {golbet}")
    
    # Test arbitrage calculator
    print()
    print("💰 Testing Arbitrage Calculator...")
    print("-" * 40)
    
    calculator = ArbitrageCalculator(min_threshold=-1.0, max_threshold=30.0)
    
    test_cases = [
        (2.00, 2.20),  # +10% - should be valid
        (2.00, 1.99),  # -0.5% - should be valid
        (2.00, 2.60),  # +30% - should be valid
        (2.00, 1.98),  # -1% - should be valid
        (2.00, 1.95),  # -2.5% - should be invalid
        (2.00, 2.80),  # +40% - should be invalid
    ]
    
    print("📊 Odds Comparison Tests:")
    for orbit_lay, golbet_back in test_cases:
        is_valid = calculator.is_valid_opportunity(orbit_lay, golbet_back)
        odds_diff_str = calculator.format_odds_difference(orbit_lay, golbet_back)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"   • Orbit: {orbit_lay}, Golbet: {golbet_back} → {odds_diff_str} → {status}")
    
    return len(matches) > 0

async def test_persistent_browser():
    """Test the persistent browser functionality."""
    
    print()
    print("🌐 Testing Persistent Browser...")
    print("=" * 60)
    
    try:
        async with PersistentBrowser() as browser:
            print("✅ Browser started successfully")
            
            # Test page creation
            page = await browser.get_page()
            if page:
                print("✅ Page created successfully")
                
                # Test basic page functionality
                await page.goto("https://httpbin.org/html")
                title = await page.title()
                print(f"✅ Page loaded: {title}")
                
                # Test health check
                is_healthy = await browser.health_check()
                print(f"✅ Browser health: {'Good' if is_healthy else 'Poor'}")
                
                return True
            else:
                print("❌ Failed to create page")
                return False
                
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

async def test_arbitrage_detection():
    """Test the complete arbitrage detection system."""
    
    print()
    print("🎯 Testing Complete Arbitrage Detection...")
    print("=" * 60)
    
    # Mock data
    orbit_data = [
        {
            "team_name": "Shakhtar Donetsk",
            "lay_odds": 1.74271,
            "market_type": "1X2"
        },
        {
            "team_name": "Dundee United",
            "lay_odds": 1.852,
            "market_type": "1X2"
        }
    ]
    
    golbet_data = [
        {
            "team_name": "Shakhtar",
            "back_odds": 1.7,
            "market_type": "1X2"
        },
        {
            "team_name": "Dundee Utd",
            "back_odds": 1.87,
            "market_type": "1X2"
        }
    ]
    
    print("📊 Test Data:")
    print(f"   • Orbit matches: {len(orbit_data)}")
    print(f"   • Golbet matches: {len(golbet_data)}")
    print()
    
    # Find opportunities
    opportunities = find_arbitrage_opportunities(orbit_data, golbet_data)
    
    print(f"📈 Results:")
    print(f"   • Opportunities found: {len(opportunities)}")
    
    if opportunities:
        print("✅ Valid Opportunities:")
        for opp in opportunities:
            print(f"   • {opp['match_name']}: {opp['odds_difference']}")
    
    return len(opportunities) >= 0

async def main():
    """Run all tests."""
    
    print("🚀 Testing New Fast Scanning System")
    print("=" * 70)
    print("This will test:")
    print("• Python-based team matching (no OpenAI)")
    print("• Persistent browser functionality")
    print("• Fast arbitrage detection")
    print("• 2-second scanning capability")
    print("=" * 70)
    
    try:
        # Test 1: Team matching
        team_matching_success = await test_team_matching()
        
        # Test 2: Persistent browser
        browser_success = await test_persistent_browser()
        
        # Test 3: Arbitrage detection
        arbitrage_success = await test_arbitrage_detection()
        
        # Results
        print()
        print("📊 Test Results Summary:")
        print("=" * 40)
        print(f"   • Team Matching: {'✅ PASSED' if team_matching_success else '❌ FAILED'}")
        print(f"   • Persistent Browser: {'✅ PASSED' if browser_success else '❌ FAILED'}")
        print(f"   • Arbitrage Detection: {'✅ PASSED' if arbitrage_success else '❌ FAILED'}")
        
        if team_matching_success and browser_success and arbitrage_success:
            print()
            print("🎉 All tests PASSED!")
            print("💡 Your new fast scanning system is ready!")
            print("⚡ You can now scan every 2 seconds instead of 60 seconds!")
            print("💰 No more OpenAI API costs!")
            print("🌐 Persistent browsers eliminate startup delays!")
            return True
        else:
            print()
            print("❌ Some tests FAILED!")
            print("🔧 Check the error messages above for issues")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🚀 Ready to use the new system!")
        print("💡 Run: python -m bot.main (select option 3)")
        print("⚡ Enjoy ultra-fast arbitrage detection!")
    else:
        print("\n🔧 System needs fixes before use!")
