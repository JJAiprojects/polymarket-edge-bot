#!/usr/bin/env python
"""Quick script to check what's in the database."""
from src.database import Database, Market, HistoricalProbability, FlaggedOpportunity

db = Database()
session = db.get_session()

# Check markets
markets = session.query(Market).all()
print(f"\n=== Markets Stored: {len(markets)} ===")
for m in markets[:5]:
    print(f"  - {m.question[:70]}...")
    print(f"    Probability: {m.current_probability:.1%}, Volume 24h: ${m.volume_24h:,.0f}")

# Check historical probabilities
hist = session.query(HistoricalProbability).all()
print(f"\n=== Historical Probability Snapshots: {len(hist)} ===")
if hist:
    print(f"  Latest: Market {hist[-1].market_id}, Prob: {hist[-1].probability:.1%}, Vol: ${hist[-1].volume_24h:,.0f}")

# Check flagged opportunities
opps = session.query(FlaggedOpportunity).all()
print(f"\n=== Flagged Opportunities: {len(opps)} ===")
for opp in opps[:3]:
    print(f"  - {opp.market_question[:60]}...")
    print(f"    Signal: {opp.signal_type}, EV: ${opp.expected_value:.2f}")

session.close()
