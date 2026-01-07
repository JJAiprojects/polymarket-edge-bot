# Fresh Wallet Large Bet Detection

## Overview

This feature detects suspicious patterns from fresh wallets making large bets - a pattern that often indicates insider information or early signals. This is based on real-world examples like the Taiwan invasion bet where a fresh account made a $300K bet.

## How It Works

The detector looks for wallets that meet ALL of these criteria:

1. **Fresh Wallet**: Wallet age ≤ 72 hours (configurable)
2. **Large Bet**: Bet size ≥ $5,000 (configurable)
3. **Single-Market Focus**: ≤ 3 total trades across all markets
4. **High Allocation**: ≥ 80% of wallet's activity is on this one market
5. **No Prior Large Bets**: Wallet hasn't made large bets on other markets before

## Configuration Parameters

Add these to your `config/config.yaml`:

```yaml
# Fresh Wallet Large Bet Detection (Insider Signals)
fresh_wallet_age_hours: 72  # 48-72 hours for "fresh" wallets
min_fresh_wallet_bet_usd: 5000  # $5k-$10k minimum bet size
fresh_wallet_max_trades: 3  # <3 total trades (single-market focus)
fresh_wallet_min_allocation_pct: 80.0  # >80% allocation to one outcome
fresh_wallet_enabled: true
```

## Requirements

- **PolygonScan API Key**: Required to check wallet age. Add to `.env`:
  ```
  POLYGONSCAN_API_KEY=your_key_here
  ```

## Notification Format

When a fresh wallet large bet is detected, you'll receive a Telegram message with:

- Wallet address (truncated for privacy)
- Wallet age in hours
- Bet size in USD
- Total trades count
- Allocation percentage
- Links to Polymarket and PolygonScan

## Example Alert

```
🚨 FRESH WALLET LARGE BET DETECTED!

Market: Will China invade Taiwan in 2025?
Signal Type: Fresh Wallet Large Bet (Insider Pattern)

⚠️ Key Details:
• Wallet: 0x12345678...abcdef
• Wallet Age: 24.0 hours (FRESH)
• Bet Size: $300,000.00
• Total Trades: 1 (single-market focus)
• Allocation: 100.0% to this market
• Current Probability: 15.2%
• Expected Value: $45.50
• Suggested Size: $500.00

Why This Matters:
This pattern (new wallet + large bet + single-market focus) often indicates insider information or early signals.

Rationale:
[Detailed analysis...]

View on Polymarket
View Wallet on PolygonScan
```

## Integration with Existing Signals

This signal works alongside your existing detection:
- Volume spikes
- Probability divergence
- Unusual trade sizes
- Twitter signals

All signals are combined and evaluated together for position sizing and risk management.

## Tuning Recommendations

- **Lower `fresh_wallet_age_hours`** (e.g., 48) for more aggressive detection
- **Raise `min_fresh_wallet_bet_usd`** (e.g., 10000) to reduce false positives
- **Adjust `fresh_wallet_max_trades`** based on your noise tolerance
- **Monitor false positive rate** and adjust `fresh_wallet_min_allocation_pct` accordingly

## Expected Frequency

Based on Polymarket's $44B+ volume in 2025:
- **1-3 flags per month** in hot categories (politics, geopolitics)
- **More frequent** during major events (elections, crises)
- **Less frequent** in stable markets

## Backtesting

A Taiwan invasion scenario has been added to the backtesting suite:

```bash
python run_backtest.py --scenario taiwan
```

This simulates the exact pattern from the tweet example.
