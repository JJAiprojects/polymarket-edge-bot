#!/usr/bin/env python
"""Test Polymarket API directly."""
from src.data_ingestion import PolymarketAPI
import json

api = PolymarketAPI()

print("=== Testing Polymarket API ===\n")

# Get markets
markets = api.get_markets(category='politics', active=True, limit=5)
print(f"Fetched {len(markets)} markets\n")

if markets:
    print("Sample market structure:")
    sample = markets[0]
    print(json.dumps(sample, indent=2, default=str)[:500])
    print("\n...")
    
    print("\n=== Market Details ===")
    for i, m in enumerate(markets[:3], 1):
        print(f"\n{i}. Market ID: {m.get('id', 'N/A')}")
        print(f"   Question: {m.get('question', 'N/A')[:80]}")
        print(f"   Category: {m.get('category', 'N/A')}")
        print(f"   Volume: {m.get('volume', 'N/A')}")
        print(f"   Liquidity: {m.get('liquidity', 'N/A')}")
        print(f"   Active: {m.get('active', 'N/A')}")
