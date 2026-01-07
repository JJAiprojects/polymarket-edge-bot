#!/usr/bin/env python
"""Run backtests on historical scenarios."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.backtesting import Backtester
from src.logger_setup import setup_logger

def print_backtest_results(results: dict, scenario_name: str = ""):
    """Print backtest results in a readable format."""
    print("\n" + "=" * 70)
    if scenario_name:
        print(f"BACKTEST RESULTS: {scenario_name}")
    else:
        print("BACKTEST RESULTS")
    print("=" * 70)
    
    print(f"\nMarket: {results.get('market_question', 'Unknown')}")
    print(f"Scenario: {results.get('scenario', 'unknown')}")
    
    print(f"\n[SUMMARY]")
    print(f"   Expected Signals: {results.get('total_expected', 0)}")
    print(f"   Signals Detected: {results.get('total_opportunities', 0)}")
    print(f"   Missed Signals: {len(results.get('missed_signals', []))}")
    
    if results.get('total_expected', 0) > 0:
        detection_rate = (results.get('total_opportunities', 0) / results.get('total_expected', 1)) * 100
        print(f"   Detection Rate: {detection_rate:.1f}%")
    
    # Show detected signals
    signals = results.get('signals_detected', [])
    if signals:
        print(f"\n[OK] Signals Detected ({len(signals)}):")
        for signal in signals:
            date_str = signal.get('date', 'Unknown').strftime('%Y-%m-%d %H:%M') if hasattr(signal.get('date'), 'strftime') else str(signal.get('date', 'Unknown'))
            signal_type = signal.get('signal_type', 'unknown')
            print(f"   - {date_str}: {signal_type}")
            if 'spike_ratio' in signal:
                print(f"     Spike Ratio: {signal['spike_ratio']:.2f}x")
            if 'trades_found' in signal:
                print(f"     Large Trades: {signal['trades_found']}")
            if 'bet_size_usd' in signal:
                print(f"     Bet Size: ${signal['bet_size_usd']:,.0f}")
            if 'wallet_age_hours' in signal:
                print(f"     Wallet Age: {signal['wallet_age_hours']} hours")
            if 'wallet_address' in signal:
                print(f"     Wallet: {signal['wallet_address']}")
    
    # Show missed signals
    missed = results.get('missed_signals', [])
    if missed:
        print(f"\n[WARN] Missed Signals ({len(missed)}):")
        for miss in missed:
            date_str = miss.get('date', 'Unknown').strftime('%Y-%m-%d %H:%M') if hasattr(miss.get('date'), 'strftime') else str(miss.get('date', 'Unknown'))
            expected = miss.get('expected', 'unknown')
            reason = miss.get('reason', 'Unknown reason')
            print(f"   - {date_str}: Expected {expected}")
            print(f"     Reason: {reason}")
    
    print("\n" + "=" * 70)

def print_summary(summary: dict):
    """Print summary of multiple backtests."""
    print("\n" + "=" * 70)
    print("BACKTEST SUMMARY - ALL SCENARIOS")
    print("=" * 70)
    
    print(f"\n[STATISTICS] Overall Statistics:")
    print(f"   Scenarios Tested: {summary.get('scenarios_tested', 0)}")
    print(f"   Total Expected Signals: {summary.get('total_expected_signals', 0)}")
    print(f"   Total Signals Detected: {summary.get('total_signals_detected', 0)}")
    print(f"   Total Missed Signals: {summary.get('total_missed_signals', 0)}")
    print(f"   Overall Detection Rate: {summary.get('detection_rate_pct', 0):.1f}%")
    
    print(f"\n[SCENARIOS] Per-Scenario Results:")
    for result in summary.get('scenario_results', []):
        scenario = result.get('scenario', 'unknown')
        detected = result.get('total_opportunities', 0)
        expected = result.get('total_expected', 0)
        rate = (detected / expected * 100) if expected > 0 else 0
        print(f"   - {scenario}: {detected}/{expected} ({rate:.1f}%)")
    
    print("\n" + "=" * 70)

def main():
    """Run backtests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest Polymarket bot on historical scenarios')
    parser.add_argument('--scenario', choices=['election', 'crypto', 'sports', 'taiwan', 'all'], 
                       default='all', help='Which scenario to test')
    parser.add_argument('--thresholds', action='store_true',
                       help='Test with different threshold settings')
    
    args = parser.parse_args()
    
    logger = setup_logger('backtest', 'INFO')
    backtester = Backtester()
    
    print("\n" + "=" * 70)
    print("POLYMARKET BOT BACKTESTING")
    print("=" * 70)
    print("\nThis will test the bot's detection logic on historical scenarios")
    print("to see how many signals would have been flagged.\n")
    
    if args.scenario == 'election':
        print("Running 2024 Election Scenario Backtest...")
        results = backtester.run_2024_election_backtest()
        print_backtest_results(results, "2024 Election")
        
    elif args.scenario == 'crypto':
        from src.backtesting.historical_data import HistoricalDataSimulator
        sim = HistoricalDataSimulator()
        scenario = sim.create_crypto_crash_scenario()
        results = backtester.backtest_scenario(scenario)
        print_backtest_results(results, "Crypto Crash")
        
    elif args.scenario == 'sports':
        from src.backtesting.historical_data import HistoricalDataSimulator
        sim = HistoricalDataSimulator()
        scenario = sim.create_sports_championship_scenario()
        results = backtester.backtest_scenario(scenario)
        print_backtest_results(results, "Sports Championship")
        
    elif args.scenario == 'taiwan':
        from src.backtesting.historical_data import HistoricalDataSimulator
        sim = HistoricalDataSimulator()
        scenario = sim.create_taiwan_invasion_scenario()
        results = backtester.backtest_scenario(scenario)
        print_backtest_results(results, "Taiwan Invasion (Fresh Wallet)")
        
    else:  # all
        print("Running Full Backtest Suite...")
        summary = backtester.run_full_backtest_suite()
        print_summary(summary)
        
        # Also show individual results
        print("\n" + "=" * 70)
        print("DETAILED RESULTS BY SCENARIO")
        print("=" * 70)
        for result in summary.get('scenario_results', []):
            print_backtest_results(result)
    
    # Test with different thresholds
    if args.thresholds:
        print("\n" + "=" * 70)
        print("TESTING WITH LOWER THRESHOLDS")
        print("=" * 70)
        
        lower_thresholds = {
            'volume_spike_multiplier': 2.0,  # Lower from 4.0
            'notification_threshold_ev': 0.01,  # Lower from 0.05
            'min_trade_size_usd': 500  # Lower from 1000
        }
        
        from src.backtesting.historical_data import HistoricalDataSimulator
        sim = HistoricalDataSimulator()
        scenario = sim.create_2024_election_scenario()
        results = backtester.backtest_scenario(scenario, config_overrides=lower_thresholds)
        print_backtest_results(results, "2024 Election (Lower Thresholds)")

if __name__ == "__main__":
    main()
