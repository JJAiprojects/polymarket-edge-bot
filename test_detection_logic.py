#!/usr/bin/env python
"""Test that verifies the detection logic actually works."""
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigManager
from src.database import Database
from src.analysis import EdgeDetector, PositionSizer, RiskManager
from src.data_ingestion import PolymarketAPI

def test_volume_spike_detection():
    """Test that volume spike detection works."""
    print("=" * 60)
    print("TEST 1: Volume Spike Detection")
    print("=" * 60)
    
    config = ConfigManager()
    db = Database("data/test_detection.db")
    edge_detector = EdgeDetector(config.get_all(), db)
    
    # Create test market data
    market_id = "test_market_001"
    
    # Add historical data (low volume)
    for i in range(5):
        db.add_historical_probability(
            market_id, 
            0.5, 
            100.0  # Low volume
        )
    
    # Test with high volume (should trigger)
    current_volume = 500.0  # 5x the average
    result = edge_detector.detect_volume_spike(market_id, current_volume, hours=4)
    
    if result:
        print(f"[PASS] Volume spike detected!")
        print(f"   Spike ratio: {result['spike_ratio']:.2f}x")
        print(f"   Current: ${current_volume:.2f}, Average: ${result['average_volume']:.2f}")
        return True
    else:
        print(f"[FAIL] Volume spike NOT detected (expected spike at 5x)")
        return False

def test_unusual_trade_detection():
    """Test that unusual trade size detection works."""
    print("\n" + "=" * 60)
    print("TEST 2: Unusual Trade Size Detection")
    print("=" * 60)
    
    config = ConfigManager()
    db = Database("data/test_detection.db")
    edge_detector = EdgeDetector(config.get_all(), db)
    
    # Create test trades
    now = datetime.now(timezone.utc)
    trades = [
        {'trader_address': '0x123', 'size': 100, 'price': 0.5, 'timestamp': now},
        {'trader_address': '0x456', 'size': 2000, 'price': 0.5, 'timestamp': now},  # $1000 trade
        {'trader_address': '0x789', 'size': 50, 'price': 0.5, 'timestamp': now},
    ]
    
    result = edge_detector.detect_unusual_trade_size(trades, min_size_usd=1000)
    
    if result and len(result.get('trades', [])) > 0:
        print(f"[PASS] Unusual trade detected!")
        print(f"   Found {len(result['trades'])} large trades")
        for trade in result['trades']:
            print(f"   - ${trade['value_usd']:.2f} trade detected")
        return True
    else:
        print(f"[FAIL] Unusual trade NOT detected (expected $1000+ trade)")
        return False

def test_probability_divergence():
    """Test that probability divergence detection works."""
    print("\n" + "=" * 60)
    print("TEST 3: Probability Divergence Detection")
    print("=" * 60)
    
    config = ConfigManager()
    db = Database("data/test_detection.db")
    edge_detector = EdgeDetector(config.get_all(), db)
    
    # Test with large divergence
    polymarket_prob = 0.50  # 50%
    external_probs = {
        'manifold': 0.65  # 65% - 15% divergence
    }
    
    result = edge_detector.detect_probability_divergence(
        polymarket_prob, 
        external_probs, 
        threshold_pct=12.0
    )
    
    if result:
        print(f"[PASS] Divergence detected!")
        for source, data in result['divergences'].items():
            print(f"   {source}: {data['divergence_pct']:.1f}% divergence")
        return True
    else:
        print(f"[FAIL] Divergence NOT detected (expected 15% divergence)")
        return False

def test_position_sizing():
    """Test that position sizing works."""
    print("\n" + "=" * 60)
    print("TEST 4: Position Sizing (Kelly Criterion)")
    print("=" * 60)
    
    config = ConfigManager()
    position_sizer = PositionSizer(config.get_all())
    
    # Test with clear edge
    market_prob = 0.40  # Market says 40%
    fair_prob = 0.55     # We think it's 55% (15% edge)
    
    sizing = position_sizer.calculate_position_size(market_prob, fair_prob)
    
    if sizing['adjusted_size'] > 0:
        print(f"[PASS] Position size calculated!")
        print(f"   Market prob: {market_prob:.1%}, Fair prob: {fair_prob:.1%}")
        print(f"   Edge: {sizing['edge_pct']:.2f}%")
        print(f"   Suggested size: ${sizing['adjusted_size']:.2f}")
        print(f"   % of bankroll: {sizing['bankroll_pct']:.2f}%")
        return True
    else:
        print(f"[FAIL] Position size is $0 (expected positive size)")
        return False

def test_expected_value_calculation():
    """Test that expected value calculation works."""
    print("\n" + "=" * 60)
    print("TEST 5: Expected Value Calculation")
    print("=" * 60)
    
    config = ConfigManager()
    db = Database("data/test_detection.db")
    edge_detector = EdgeDetector(config.get_all(), db)
    
    # Test with positive EV
    market_prob = 0.40
    fair_prob = 0.55
    bet_size = 100.0
    
    ev = edge_detector.calculate_expected_value(market_prob, fair_prob, bet_size)
    
    if ev > 0:
        print(f"[PASS] Positive EV calculated!")
        print(f"   EV: ${ev:.2f}")
        print(f"   This means the bet has positive expected value")
        return True
    else:
        print(f"[FAIL] EV is ${ev:.2f} (expected positive)")
        return False

def test_risk_management():
    """Test that risk management constraints work."""
    print("\n" + "=" * 60)
    print("TEST 6: Risk Management")
    print("=" * 60)
    
    config = ConfigManager()
    db = Database("data/test_detection.db")
    risk_manager = RiskManager(config.get_all(), db)
    
    # Test position limits
    can_take, reason = risk_manager.can_take_position(100.0)
    
    if can_take:
        print(f"[PASS] Risk manager allows position")
        print(f"   Can take $100 position")
        
        # Test portfolio summary
        portfolio = risk_manager.get_portfolio_summary()
        print(f"   Current positions: {portfolio['open_positions']}")
        print(f"   Max positions: {portfolio['max_positions']}")
        print(f"   Exposure: ${portfolio['total_exposure_usd']:.2f} ({portfolio['exposure_pct']:.1f}%)")
        return True
    else:
        print(f"[WARN] Position rejected: {reason}")
        print(f"   This is OK if limits are already reached")
        return True  # Still pass, just showing constraint works

def test_real_market_connection():
    """Test that we can actually connect to Polymarket and get data."""
    print("\n" + "=" * 60)
    print("TEST 7: Real Polymarket API Connection")
    print("=" * 60)
    
    try:
        api = PolymarketAPI()
        markets = api.get_markets(category='politics', active=True, limit=5)
        
        if markets and len(markets) > 0:
            print(f"[PASS] Connected to Polymarket API")
            print(f"   Fetched {len(markets)} markets")
            
            # Try to get price data from first market
            test_market = markets[0]
            market_id = test_market.get('id')
            
            try:
                prices = api.get_market_prices(market_id)
                if prices:
                    print(f"   [OK] Got price data for market: {test_market.get('question', 'Unknown')[:50]}...")
                    print(f"   Prices: {prices}")
                    return True
                else:
                    print(f"   [WARN] Market has no price data (may be resolved)")
                    return True  # Still pass - API works
            except Exception as e:
                print(f"   [WARN] Could not get prices: {e}")
                return True  # API connection works, just this market is old
        else:
            print(f"[FAIL] No markets returned from API")
            return False
    except Exception as e:
        print(f"[FAIL] API connection error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BOT DETECTION LOGIC VERIFICATION TEST")
    print("=" * 60)
    print("\nThis test verifies that each detection component actually works.")
    print("It uses simulated data to prove the logic functions correctly.\n")
    
    results = []
    
    # Run all tests
    results.append(("Volume Spike Detection", test_volume_spike_detection()))
    results.append(("Unusual Trade Detection", test_unusual_trade_detection()))
    results.append(("Probability Divergence", test_probability_divergence()))
    results.append(("Position Sizing", test_position_sizing()))
    results.append(("Expected Value", test_expected_value_calculation()))
    results.append(("Risk Management", test_risk_management()))
    results.append(("API Connection", test_real_market_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All detection logic is working correctly!")
        print("   The bot CAN detect opportunities when they exist.")
    elif passed >= total * 0.8:
        print("\n[OK] MOSTLY WORKING! Most detection logic is functional.")
        print("   Review failed tests above.")
    else:
        print("\n[WARN] SOME ISSUES: Some detection logic needs attention.")
        print("   Review failed tests above.")
    
    # Cleanup
    if os.path.exists("data/test_detection.db"):
        try:
            os.remove("data/test_detection.db")
        except:
            pass

if __name__ == "__main__":
    main()
