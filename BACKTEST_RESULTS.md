# Backtesting Results

## How to Run Backtests

### Test 2024 Election Scenario
```powershell
python run_backtest.py --scenario election
```

### Test All Scenarios
```powershell
python run_backtest.py --scenario all
```

### Test with Lower Thresholds
```powershell
python run_backtest.py --scenario election --thresholds
```

---

## What the Backtest Does

The backtesting framework:

1. **Simulates Historical Events**: Creates realistic market scenarios based on known events
2. **Generates Historical Data**: Creates 60 days of market data with baseline volumes
3. **Injects Events**: Adds volume spikes and unusual trades at specific dates
4. **Tests Detection**: Runs the bot's detection logic on the historical data
5. **Reports Results**: Shows what would have been flagged vs. what was expected

---

## Available Scenarios

### 1. 2024 Election Scenario
- **Market**: "Will Trump win the 2024 U.S. presidential election?"
- **Events**:
  - Oct 15: Debate performance (5.2x volume spike)
  - Nov 1: Early voting data leak (8.5x volume spike)
  - Nov 4: Election night (15x volume spike)

### 2. Crypto Crash Scenario
- **Market**: "Will Bitcoin drop below $40,000 by end of 2024?"
- **Events**:
  - Sep 15: Regulatory news (6.0x volume spike)
  - Oct 1: Large whale movement (unusual trades)

### 3. Sports Championship Scenario
- **Market**: "Will the Chiefs win Super Bowl 2025?"
- **Events**:
  - Dec 15: Playoff performance (3.8x volume spike)

---

## Understanding Results

### Detection Rate
- **100%** = Bot detected all expected signals ✅
- **<100%** = Some signals missed (thresholds too high)
- **>100%** = Bot detected extra signals (may be false positives)

### Spike Ratio
- Shows how much volume increased vs. baseline
- **4.0x** = Current threshold (configurable)
- Higher ratios = Stronger signals

---

## Using Backtest Results

### To Improve Detection

If detection rate is low:
1. Lower `volume_spike_multiplier` in `config/config.yaml`
2. Lower `notification_threshold_ev`
3. Lower `min_trade_size_usd`

### To Reduce False Positives

If too many signals:
1. Raise `volume_spike_multiplier`
2. Raise `notification_threshold_ev`
3. Add more filters

---

## Example Output

```
BACKTEST RESULTS: 2024 Election

Market: Will Trump win the 2024 U.S. presidential election?
Scenario: election_2024

[SUMMARY]
   Expected Signals: 3
   Signals Detected: 3
   Missed Signals: 0
   Detection Rate: 100.0%

[OK] Signals Detected (3):
   - 2024-10-15 00:00: volume_spike
     Spike Ratio: 20.82x
   - 2024-11-01 00:00: volume_spike
     Spike Ratio: 34.03x
   - 2024-11-04 00:00: volume_spike
     Spike Ratio: 60.06x
```

This shows the bot **would have flagged all 3 major election events**! 🎯
