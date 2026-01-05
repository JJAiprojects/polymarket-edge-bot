# Bot Parameters & Thresholds Reference

This document lists all parameters the bot checks and the thresholds that trigger alerts.

---

## 📊 Volume Spike Detection

**What it checks:** Unusual trading volume spikes in markets

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `volume_spike_multiplier` | **4.0x** | Volume spike threshold | Current volume ≥ 4x average volume |
| `volume_spike_time_window_hours` | **4 hours** | Time window for spike detection | Volume over last 4 hours |
| `niche_liquidity_threshold_usd` | **$50,000** | Maximum liquidity for "niche" markets | Markets with <$50k daily volume |

**How it works:**
- Compares current 4-hour volume to 24-hour average volume
- Flags if volume is 4x or more than average
- More sensitive in niche/low-liquidity markets

---

## 📈 Probability Divergence Detection

**What it checks:** Differences between Polymarket and external sources (Manifold, Metaculus)

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `divergence_threshold_pct` | **12.0%** | Minimum divergence to flag | |Polymarket prob - External prob| ≥ 12% |

**How it works:**
- Compares Polymarket probability with Manifold Markets
- Flags if difference is 12% or more
- Suggests potential mispricing opportunity

---

## 👛 Smart Wallet Tracking

**What it checks:** Activity from wallets with proven track records

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `wallet_age_hours` | **24 hours** | Age threshold for "fresh" wallets | Wallet age < 24 hours |
| `wallet_success_rate_threshold` | **70%** | Minimum success rate | Success rate ≥ 70% |
| `wallet_min_trades_to_qualify` | **10 trades** | Minimum trades to be considered | Total trades ≥ 10 |
| `min_trade_size_usd` | **$1,000** | Minimum trade size to flag | Trade value ≥ $1,000 |

**How it works:**
- Tracks wallets with ≥10 trades and ≥70% success rate
- Flags trades from these "smart wallets"
- Also flags unusually large trades (≥$1,000)

---

## 💰 Position Sizing (Kelly Criterion)

**What it checks:** Optimal bet sizing based on edge and bankroll

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `kelly_fraction` | **0.5** (Half-Kelly) | Fractional Kelly multiplier | Uses 50% of full Kelly |
| `max_exposure_pct` | **40%** | Maximum portfolio exposure | Total exposure ≤ 40% of bankroll |
| `bankroll_size_usd` | **$10,000** | Total bankroll size | Used for position calculations |
| `correlation_reduction_factor` | **0.5** | Size reduction for correlated bets | Reduces size by 50% if correlated |

**How it works:**
- Calculates optimal position size using Kelly Criterion
- Uses fractional Kelly (50%) for safety
- Caps total exposure at 40% of bankroll
- Reduces size by 50% for correlated positions

---

## 🎯 Market Selection Filters

**What it checks:** Criteria for which markets to analyze

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `min_liquidity_usd` | **$0** (testing) | Minimum market liquidity | Liquidity ≥ $0 (normally $5,000) |
| `max_niche_liquidity_usd` | **$100,000** | Maximum for niche markets | Liquidity ≤ $100k for niche focus |
| `min_days_to_resolution` | **30 days** | Minimum time until resolution | Days to resolution ≥ 30 |
| `avoid_coin_flip_range` | **5%** | Skip 50/50 markets | Skip if prob between 45-55% |

**How it works:**
- Only analyzes markets with sufficient liquidity
- Prefers markets resolving in 30+ days
- Skips pure coin-flip markets (45-55% probability) without thesis

---

## 🔗 Correlation Analysis

**What it checks:** Relationships between correlated markets

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `correlation_threshold` | **0.7** | Minimum correlation coefficient | |Correlation| ≥ 0.7 |
| `correlation_movement_delta_pct` | **5.0%** | Movement threshold for divergence | One market moves ≥5% without other |
| `correlation_window_days` | **7 days** | Historical window for correlation | Uses last 7 days of data |

**How it works:**
- Calculates correlation between markets over 7 days
- Flags if one market moves ≥5% without correlated market moving
- Suggests potential arbitrage or early signal

---

## ⚠️ Risk Management

**What it checks:** Portfolio risk limits and constraints

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `hedge_threshold` | **70%** | Probability threshold for hedging | Position prob ≥ 70% |
| `max_hedge_size_pct` | **20%** | Maximum hedge size | Hedge ≤ 20% of position |
| `stop_loss_prob_drop_pct` | **20%** | Stop-loss threshold | Probability drops ≥20% from entry |
| `max_open_positions` | **10** | Maximum concurrent positions | Total positions ≤ 10 |

**How it works:**
- Limits total open positions to 10
- Suggests hedging when probability ≥70%
- Triggers stop-loss if probability drops 20% from entry
- Enforces maximum exposure limits

---

## 🐦 Twitter Signal Detection

**What it checks:** Social media activity for market-related keywords

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `twitter_min_mentions` | **15** | Minimum mentions to trigger | Mentions ≥ 15 in time window |
| `twitter_time_window_hours` | **1 hour** | Time window for mentions | Mentions in last 1 hour |
| `twitter_enabled` | **true** | Enable/disable Twitter monitoring | Must be true to check |

**How it works:**
- Searches Twitter for market-related keywords
- Flags if ≥15 mentions in last hour
- Suggests early social media signals

---

## 🔔 Notification Thresholds

**What it checks:** Minimum criteria to send notifications

| Parameter | Current Value | Description | Trigger Condition |
|-----------|--------------|-------------|-------------------|
| `notification_threshold_ev` | **$0.05** | Minimum expected value | Expected value ≥ $0.05 |
| `telegram_enabled` | **true** | Enable Telegram notifications | Must be true |
| `discord_enabled` | **false** | Enable Discord notifications | Currently disabled |

**How it works:**
- Only flags opportunities with EV ≥ $0.05
- Sends Telegram notifications if enabled
- Filters out low-value opportunities

---

## ⏱️ Polling Configuration

| Parameter | Current Value | Description |
|-----------|--------------|-------------|
| `poll_interval_minutes` | **15 minutes** | How often bot runs analysis |

---

## 📁 Market Categories Monitored

Currently monitoring:
- **politics**
- **crypto**
- **sports**
- **entertainment**

---

## 🔧 API Rate Limits

| Parameter | Current Value | Description |
|-----------|--------------|-------------|
| `polymarket_rate_limit` | **60 req/min** | Polymarket API rate limit |
| `twitter_rate_limit` | **15 req/min** | Twitter API rate limit |
| `polygonscan_rate_limit` | **5 req/min** | PolygonScan API rate limit |

---

## 📝 Summary: What Triggers an Alert?

An opportunity is flagged when **ALL** of these conditions are met:

1. ✅ **Signal Detected** (one of):
   - Volume spike ≥4x average
   - Probability divergence ≥12% from external source
   - Smart wallet activity detected
   - Twitter mentions ≥15 in 1 hour
   - Unusual trade size ≥$1,000
   - Correlation divergence (one market moves ≥5% without correlated market)

2. ✅ **Expected Value** ≥ $0.05

3. ✅ **Risk Limits**:
   - Total positions < 10
   - Total exposure < 40% of bankroll
   - Position size within Kelly Criterion limits

4. ✅ **Market Meets Criteria**:
   - Sufficient liquidity
   - Resolves in 30+ days
   - Not a pure coin-flip (unless has thesis)

---

## 🎛️ How to Adjust Thresholds

Edit `config/config.yaml` to change any parameter:

**More Sensitive (more alerts):**
- Lower `volume_spike_multiplier` (e.g., 3.0)
- Lower `divergence_threshold_pct` (e.g., 8.0)
- Lower `notification_threshold_ev` (e.g., 0.01)
- Lower `twitter_min_mentions` (e.g., 10)

**Less Sensitive (fewer alerts):**
- Raise `volume_spike_multiplier` (e.g., 5.0)
- Raise `divergence_threshold_pct` (e.g., 15.0)
- Raise `notification_threshold_ev` (e.g., 0.10)
- Raise `twitter_min_mentions` (e.g., 20)

---

## 📊 Current Status

Based on your last run:
- ✅ Bot analyzed **200 markets**
- ✅ No opportunities detected (normal - means no edges met thresholds)
- ✅ Portfolio: **0 positions**, **$0.00 exposure**

This is expected! The bot only flags real edges, not every market movement.
