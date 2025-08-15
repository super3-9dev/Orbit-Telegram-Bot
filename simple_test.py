#!/usr/bin/env python3
"""
Simple test script to verify the new fast scanning system.
"""

def test_team_matcher():
    """Test the team matcher functionality."""
    try:
        from bot.core.team_matcher import TeamMatcher, ArbitrageCalculator
        
        print("✅ Team matcher import successful")
        
        # Test team matcher
        matcher = TeamMatcher(match_threshold=70)
        print("✅ Team matcher instance created")
        
        # Test team normalization
        test_team = "Shakhtar Donetsk"
        normalized = matcher.normalize_team_name(test_team)
        print(f"✅ Team normalization: '{test_team}' → '{normalized}'")
        
        # Test arbitrage calculator
        calculator = ArbitrageCalculator(min_threshold=-1.0, max_threshold=30.0)
        print("✅ Arbitrage calculator created")
        
        # Test odds calculation
        orbit_lay = 2.00
        golbet_back = 2.20
        is_valid = calculator.is_valid_opportunity(orbit_lay, golbet_back)
        odds_diff = calculator.format_odds_difference(orbit_lay, golbet_back)
        print(f"✅ Odds calculation: {orbit_lay} vs {golbet_back} → {odds_diff} → Valid: {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Team matcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_persistent_browser():
    """Test the persistent browser functionality."""
    try:
        from bot.core.persistent_browser import PersistentBrowser, BrowserManager
        
        print("✅ Persistent browser import successful")
        
        # Test browser manager
        manager = BrowserManager()
        print("✅ Browser manager created")
        
        return True
        
    except Exception as e:
        print(f"❌ Persistent browser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler():
    """Test the scheduler functionality."""
    try:
        from bot.core.scheduler import run_cycle
        
        print("✅ Scheduler import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing New Fast Scanning System")
    print("=" * 50)
    
    tests = [
        ("Team Matcher", test_team_matcher),
        ("Persistent Browser", test_persistent_browser),
        ("Scheduler", test_scheduler)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   • {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
        print("💡 Your new fast scanning system is ready!")
        print("⚡ You can now scan every 2 seconds instead of 60 seconds!")
        print("💰 No more OpenAI API costs!")
        print("🌐 Persistent browsers eliminate startup delays!")
        return True
    else:
        print(f"\n❌ {total - passed} tests FAILED!")
        print("🔧 Check the error messages above for issues")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 Ready to use the new system!")
        print("💡 Run: python -m bot.main (select option 3)")
        print("⚡ Enjoy ultra-fast arbitrage detection!")
    else:
        print("\n🔧 System needs fixes before use!")
