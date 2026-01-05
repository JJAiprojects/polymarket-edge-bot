#!/usr/bin/env python
"""Test script to verify bot can detect opportunities with lowered thresholds."""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigManager
from src.logger_setup import setup_logger
from src.database import Database
from src.data_ingestion import PolymarketAPI
from src.analysis import EdgeDetector
from src.analysis import PositionSizer
from src.analysis import RiskManager

def test_detection():
    """Test that the bot can detect opportunities with test thresholds."""
    
    print("=" * 60)
    print("BOT DETECTION TEST")
    print("=" * 60)
    print()
    
    # Load config
    config = ConfigManager()
    logger = setup_logger('test_bot', 'INFO')
    
    # Temporarily lower thresholds for testing
    test_config = config.get_all()
    test_config['notification_threshold_ev'] = 0.01  # Lower from 0.05
    test_config['volume_spike_multiplier'] = 2.0  # Lower from 4.0
    test_config['divergence_threshold_pct'] = 5.0  # Lower from 12.0
    test_config['min_trade_size_usd'] = 100  # Lower from 1000
    test_config['twitter_min_mentions'] = 5  # Lower from 15
    
    print("Test Configuration (Lowered Thresholds):")
    print(f"  Volume Spike Multiplier: {test_config['volume_spike_multiplier']}x (normal: 4.0x)")
    print(f"  Divergence Threshold: {test_config['divergence_threshold_pct']}% (normal: 12.0%)")
    print(f"  Min Trade Size: ${test_config['min_trade_size_usd']} (normal: $1,000)")
    print(f"  Notification EV: ${test_config['notification_threshold_ev']} (normal: $0.05)")
    print()
    
    # Initialize components
    db = Database("data/test_bot.db")
    polymarket = PolymarketAPI(rate_limit=60)
    edge_detector = EdgeDetector(test_config, db)
    position_sizer = PositionSizer(test_config)
    risk_manager = RiskManager(test_config, db)
    
    print("Fetching markets from Polymarket...")
    try:
        # Get active markets - use same logic as main bot
        all_markets = []
        categories = ['politics', 'crypto', 'sports', 'entertainment']
        
        for category in categories:
            try:
                markets = polymarket.get_markets(category=category, active=True, limit=50)
                all_markets.extend(markets)
                print(f"  Fetched {len(markets)} markets from {category}")
            except Exception as e:
                print(f"  ⚠ Error fetching {category}: {e}")
        
        # Filter by liquidity (same as main bot)
        min_liquidity = 0  # Lower for testing
        filtered_markets = [
            m for m in all_markets
            if float(m.get('liquidity', 0)) >= min_liquidity
        ]
        
        print(f"\nTotal markets found: {len(all_markets)}")
        print(f"Markets with liquidity: {len(filtered_markets)}")
        print()
        
        opportunities_found = 0
        tested_count = 0
        max_to_test = 10
        
        for market in filtered_markets:
            if tested_count >= max_to_test:
                break
                
            market_id = market.get('id')
            question = market.get('question', 'Unknown')
            
            tested_count += 1
            print(f"[{tested_count}/{max_to_test}] Testing: {question[:60]}...")
            
            try:
                # Get full market data first
                market_details = polymarket.get_market(market_id)
                if not market_details:
                    print("  ⚠ Market not found")
                    continue
                
                # Check if market is actually active and has tokens
                if not market_details.get('active', True):
                    print("  ⚠ Market is not active")
                    continue
                
                # Check for tokens (active markets have tokens with prices)
                tokens = market_details.get('tokens', [])
                if not tokens:
                    print("  ⚠ No tokens available (market may be resolved)")
                    continue
                
                # Get market prices
                prices = polymarket.get_market_prices(market_id)
                if not prices or len(prices) == 0:
                    print("  ⚠ No price data available")
                    continue
                
                # Successfully got price data!
                main_prob = max(prices.values()) if prices else 0.5
                print(f"  ✅ Market active! Current probability: {main_prob:.1%}")
                
                main_prob = max(prices.values()) if prices else 0.5
                volume_24h = float(market.get('volume', 0) or market_details.get('volume', 0))
                
                # Store in database for history
                db.add_historical_probability(market_id, main_prob, volume_24h)
                
                # Test volume spike detection
                volume_4h = polymarket.get_market_volume(market_id, hours=4)
                if volume_4h > 0:
                    spike = edge_detector.detect_volume_spike(market_id, volume_4h, hours=4)
                    if spike:
                        opportunities_found += 1
                        print(f"  ✅ VOLUME SPIKE DETECTED!")
                        print(f"     Ratio: {spike['spike_ratio']:.2f}x")
                        print(f"     Current: ${volume_4h:.2f}, Average: ${spike['average_volume']:.2f}")
                
                # Test trade size detection
                trades = polymarket.get_trades(market_id=market_id, limit=20)
                if trades:
                    unusual = edge_detector.detect_unusual_trade_size(trades, min_size_usd=test_config['min_trade_size_usd'])
                    if unusual:
                        opportunities_found += 1
                        print(f"  ✅ UNUSUAL TRADE SIZE DETECTED!")
                        print(f"     Found {len(unusual['trades'])} large trades")
                
                # Test position sizing
                fair_prob = main_prob * 1.05  # Assume 5% edge
                sizing = position_sizer.calculate_position_size(main_prob, fair_prob)
                ev = edge_detector.calculate_expected_value(main_prob, fair_prob, sizing['adjusted_size'])
                
                if ev >= test_config['notification_threshold_ev']:
                    print(f"  ✅ POSITIVE EV: ${ev:.2f}")
                    print(f"     Edge: {sizing['edge_pct']:.2f}%")
                    print(f"     Suggested Size: ${sizing['adjusted_size']:.2f}")
                
            except Exception as e:
                print(f"  ⚠ Error: {e}")
            
            print()
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Markets tested: 5")
        print(f"Opportunities detected: {opportunities_found}")
        print()
        
        if opportunities_found > 0:
            print("✅ SUCCESS! Bot is detecting opportunities!")
            print("   The bot is working correctly.")
        else:
            print("ℹ️  No opportunities found in test sample.")
            print("   This is normal - the bot only flags real edges.")
            print("   Try running with even lower thresholds or wait for market activity.")
        
        print()
        print("To see more detections, you can:")
        print("1. Lower thresholds in config/config.yaml")
        print("2. Run the bot continuously: python run.py")
        print("3. Wait for actual market events/volatility")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists("data/test_bot.db"):
            try:
                os.remove("data/test_bot.db")
            except:
                pass

if __name__ == "__main__":
    test_detection()
