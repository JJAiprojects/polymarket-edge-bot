"""Backtesting framework for the bot."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import random

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config_manager import ConfigManager
from src.database import Database
from src.analysis import EdgeDetector, PositionSizer, RiskManager, FreshWalletDetector
from src.data_ingestion.blockchain import BlockchainMonitor
from .historical_data import HistoricalDataSimulator

logger = logging.getLogger(__name__)


class Backtester:
    """Backtest the bot on historical scenarios."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize backtester.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigManager(config_path)
        self.db = Database("data/backtest.db")
        self.simulator = HistoricalDataSimulator()
        
        config_dict = self.config.get_all()
        self.edge_detector = EdgeDetector(config_dict, self.db)
        self.position_sizer = PositionSizer(config_dict)
        self.risk_manager = RiskManager(config_dict, self.db)
        
        # Initialize blockchain monitor for fresh wallet detection
        polygon_rpc = self.config.get('polygon_rpc_url', 'https://polygon-rpc.com')
        polygonscan_key = self.config.get('polygonscan_api_key')
        blockchain_monitor = BlockchainMonitor(polygon_rpc, polygonscan_key)
        self.fresh_wallet_detector = FreshWalletDetector(config_dict, self.db, blockchain_monitor)
    
    def backtest_scenario(
        self,
        scenario: Dict[str, Any],
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Backtest a specific scenario.
        
        Args:
            scenario: Scenario dictionary from HistoricalDataSimulator
            config_overrides: Optional config overrides for testing
            
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Backtesting scenario: {scenario.get('scenario', 'unknown')}")
        
        # Override config if needed
        if config_overrides:
            for key, value in config_overrides.items():
                self.config.config[key] = value
        
        market_id = scenario['market_id']
        results = {
            'scenario': scenario.get('scenario', 'unknown'),
            'market_question': scenario.get('question', 'Unknown'),
            'signals_detected': [],
            'expected_signals': [],
            'false_positives': [],
            'missed_signals': [],
            'total_opportunities': 0,
            'total_expected': len(scenario.get('events', []))
        }
        
        # Generate historical data (more days for better baseline)
        history = self.simulator.generate_historical_market_data(scenario, days_back=60)
        
        # Store historical data in database (store baseline first)
        baseline_stored = False
        for data_point in history:
            # Store all historical data for volume spike calculation
            self.db.add_historical_probability(
                market_id,
                data_point['probability'],
                data_point['volume_24h']
            )
            baseline_stored = True
        
        # Test each event
        for event in scenario.get('events', []):
            event_date = event['date']
            expected_signal = event.get('expected_signal', 'unknown')
            results['expected_signals'].append({
                'date': event_date,
                'event': event.get('event', 'Unknown'),
                'signal_type': expected_signal
            })
            
            # Calculate volume for the 4-hour window around event
            # The event should create a spike
            base_volume = scenario.get('volume', 1000.0)
            spike_multiplier = event.get('volume_spike', 1.0)
            event_volume_4h = base_volume * spike_multiplier * 4  # 4 hours of spiked volume
            
            # Test volume spike detection
            if expected_signal == 'volume_spike':
                # Need to ensure we have baseline data before the event
                # Simulate storing baseline data points before event
                baseline_points = [
                    h for h in history 
                    if h['timestamp'] < event_date - timedelta(hours=4)
                ]
                
                # Now test detection with the spiked volume
                spike = self.edge_detector.detect_volume_spike(
                    market_id, event_volume_4h, hours=4
                )
                
                if spike:
                    results['signals_detected'].append({
                        'date': event_date,
                        'signal_type': 'volume_spike',
                        'detected': True,
                        'spike_ratio': spike.get('spike_ratio', 0),
                        'event': event.get('event', 'Unknown')
                    })
                else:
                    # Calculate what the ratio actually was
                    avg_volume = sum(h['volume_24h'] for h in baseline_points[-24:]) / len(baseline_points[-24:]) if baseline_points else base_volume
                    actual_ratio = event_volume_4h / avg_volume if avg_volume > 0 else 0
                    threshold = self.config.get('volume_spike_multiplier', 4.0)
                    
                    results['missed_signals'].append({
                        'date': event_date,
                        'expected': 'volume_spike',
                        'reason': f'Ratio {actual_ratio:.2f}x below threshold {threshold}x',
                        'actual_ratio': actual_ratio,
                        'threshold': threshold
                    })
            
            # Test unusual trade detection
            if expected_signal == 'unusual_trade_size':
                trades = self.simulator.generate_historical_trades(scenario, event_date)
                unusual = self.edge_detector.detect_unusual_trade_size(
                    trades,
                    min_size_usd=self.config.get('min_trade_size_usd', 1000)
                )
                if unusual:
                    results['signals_detected'].append({
                        'date': event_date,
                        'signal_type': 'unusual_trade_size',
                        'detected': True,
                        'trades_found': len(unusual.get('trades', []))
                    })
                else:
                    results['missed_signals'].append({
                        'date': event_date,
                        'expected': 'unusual_trade_size',
                        'reason': 'No large trades detected'
                    })
            
            # Test fresh wallet large bet detection
            if expected_signal == 'fresh_wallet_large_bet':
                # Generate trades with fresh wallet pattern
                fresh_wallet_data = event.get('fresh_wallet_bet', {})
                wallet_age = fresh_wallet_data.get('wallet_age_hours', 24)
                bet_size = fresh_wallet_data.get('bet_size_usd', 5000)
                total_trades = fresh_wallet_data.get('total_trades', 1)
                
                # Create wallet address
                wallet_address = f'0xFRESH{random.randint(1000, 9999)}'
                
                # Calculate trade size based on bet size and probability
                # Use scenario's base probability, or default to 0.5
                market_prob = scenario.get('base_probability', 0.5)
                # Trade size = bet_size / probability (to get shares worth $bet_size at current price)
                trade_size = bet_size / market_prob if market_prob > 0 else bet_size * 2
                
                # Create trade that matches pattern
                trades = [{
                    'trader_address': wallet_address,
                    'size': str(trade_size),
                    'price': str(market_prob),
                    'timestamp': event_date.isoformat() if isinstance(event_date, datetime) else str(event_date)
                }]
                
                # Store trade in database for wallet history check
                from src.database import Trade
                session = self.db.get_session()
                try:
                    # Store the trade so fresh wallet detector can check wallet history
                    trade = Trade(
                        market_id=market_id,
                        trader_address=wallet_address,
                        size=trade_size,
                        price=market_prob,
                        timestamp=event_date if isinstance(event_date, datetime) else datetime.now()
                    )
                    session.add(trade)
                    session.commit()
                except Exception as e:
                    logger.debug(f"Error storing trade: {e}")
                    session.rollback()
                finally:
                    session.close()
                
                # Mock wallet age (in real scenario, blockchain monitor would check)
                # For backtesting, we'll simulate it
                original_get_age = self.fresh_wallet_detector.blockchain.get_wallet_age
                def mock_get_age(address):
                    if 'FRESH' in address:
                        return wallet_age
                    return original_get_age(address)
                self.fresh_wallet_detector.blockchain.get_wallet_age = mock_get_age
                
                fresh_wallet_signal = self.fresh_wallet_detector.detect_fresh_wallet_large_bet(
                    market_id, trades
                )
                
                if fresh_wallet_signal:
                    results['signals_detected'].append({
                        'date': event_date,
                        'signal_type': 'fresh_wallet_large_bet',
                        'detected': True,
                        'bet_size_usd': fresh_wallet_signal.get('bet_size_usd', 0),
                        'wallet_age_hours': fresh_wallet_signal.get('wallet_age_hours', 0),
                        'wallet_address': wallet_address
                    })
                else:
                    # Check why it failed
                    reason = "Pattern not detected"
                    if bet_size < self.config.get('min_fresh_wallet_bet_usd', 5000):
                        reason = f"Bet size ${bet_size} below threshold ${self.config.get('min_fresh_wallet_bet_usd', 5000)}"
                    elif wallet_age > self.config.get('fresh_wallet_age_hours', 72):
                        reason = f"Wallet age {wallet_age}h above threshold {self.config.get('fresh_wallet_age_hours', 72)}h"
                    
                    results['missed_signals'].append({
                        'date': event_date,
                        'expected': 'fresh_wallet_large_bet',
                        'reason': reason,
                        'bet_size': bet_size,
                        'wallet_age': wallet_age
                    })
        
        results['total_opportunities'] = len(results['signals_detected'])
        
        return results
    
    def backtest_multiple_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Backtest multiple scenarios.
        
        Args:
            scenarios: List of scenario dictionaries
            config_overrides: Optional config overrides
            
        Returns:
            Summary of all backtests
        """
        all_results = []
        
        for scenario in scenarios:
            result = self.backtest_scenario(scenario, config_overrides)
            all_results.append(result)
        
        # Calculate summary statistics
        total_signals = sum(r['total_opportunities'] for r in all_results)
        total_expected = sum(r['total_expected'] for r in all_results)
        total_missed = sum(len(r['missed_signals']) for r in all_results)
        
        detection_rate = (total_signals / total_expected * 100) if total_expected > 0 else 0
        
        return {
            'scenarios_tested': len(scenarios),
            'total_signals_detected': total_signals,
            'total_expected_signals': total_expected,
            'total_missed_signals': total_missed,
            'detection_rate_pct': detection_rate,
            'scenario_results': all_results
        }
    
    def run_2024_election_backtest(self) -> Dict[str, Any]:
        """Run backtest on 2024 election scenario.
        
        Returns:
            Backtest results
        """
        scenario = self.simulator.create_2024_election_scenario()
        return self.backtest_scenario(scenario)
    
    def run_full_backtest_suite(self) -> Dict[str, Any]:
        """Run backtest on all available scenarios.
        
        Returns:
            Summary of all backtests
        """
        scenarios = [
            self.simulator.create_2024_election_scenario(),
            self.simulator.create_crypto_crash_scenario(),
            self.simulator.create_sports_championship_scenario(),
            self.simulator.create_taiwan_invasion_scenario()  # Fresh wallet detection test
        ]
        
        return self.backtest_multiple_scenarios(scenarios)
