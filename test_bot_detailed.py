#!/usr/bin/env python
"""Detailed test of bot functionality."""
from src.data_ingestion import PolymarketAPI
from src.database import Database
from src.analysis import EdgeDetector
from src.config_manager import ConfigManager

print("=== Detailed Bot Test ===\n")

# Initialize
config = ConfigManager()
api = PolymarketAPI()
db = Database()

# Get markets
print("1. Fetching markets...")
markets = api.get_markets(category='politics', active=True, limit=10)
print(f"   Fetched {len(markets)} markets")

# Check liquidity
print("\n2. Checking liquidity...")
min_liquidity = config.get('min_liquidity_usd', 5000)
markets_with_liquidity = [m for m in markets if float(m.get('liquidity', 0)) > 0]
print(f"   Markets with liquidity > 0: {len(markets_with_liquidity)}")
print(f"   Markets meeting threshold (>=${min_liquidity}): {len([m for m in markets if float(m.get('liquidity', 0)) >= min_liquidity])}")

if markets_with_liquidity:
    print("\n   Sample markets with liquidity:")
    for m in markets_with_liquidity[:3]:
        liq = float(m.get('liquidity', 0))
        vol = float(m.get('volume', 0))
        print(f"   - {m.get('question', 'N/A')[:60]}...")
        print(f"     Liquidity: ${liq:,.0f}, Volume: ${vol:,.0f}")

# Test with lower threshold
print("\n3. Testing with lower liquidity threshold (for testing)...")
test_markets = [m for m in markets if float(m.get('liquidity', 0)) >= 0]  # Accept all
print(f"   Would analyze {len(test_markets)} markets with threshold=0")

if test_markets:
    print("\n   Analyzing first market (for testing)...")
    market = test_markets[0]
    market_id = market.get('id')
    
    # Get market details
    try:
        market_details = api.get_market(market_id)
        print(f"   Market ID: {market_id}")
        print(f"   Question: {market.get('question', 'N/A')[:70]}")
        
        # Get prices
        prices = api.get_market_prices(market_id)
        if prices:
            print(f"   Prices: {prices}")
        else:
            print("   No prices available (market may be resolved)")
            
        # Get volume
        volume_4h = api.get_market_volume(market_id, hours=4)
        print(f"   4-hour volume: ${volume_4h:,.2f}")
        
    except Exception as e:
        print(f"   Error: {e}")

print("\n=== Test Complete ===")
print("\nNote: Most markets have liquidity=0, so they're filtered out.")
print("This is normal - the bot only analyzes markets with sufficient liquidity.")
print("\nTo see the bot in action, either:")
print("1. Wait for markets with higher liquidity to appear")
print("2. Temporarily lower min_liquidity_usd in config/config.yaml")
