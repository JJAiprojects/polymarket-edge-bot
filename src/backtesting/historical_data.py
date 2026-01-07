"""Historical data simulator for backtesting."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class HistoricalDataSimulator:
    """Simulate historical market conditions for backtesting."""
    
    @staticmethod
    def create_2024_election_scenario() -> Dict[str, Any]:
        """Create simulated 2024 election market scenario.
        
        Returns:
            Dictionary with market data and expected signals
        """
        return {
            'market_id': 'election_2024_sim',
            'question': 'Will Trump win the 2024 U.S. presidential election?',
            'category': 'politics',
            'active': True,
            'liquidity': 50000.0,
            'volume': 10000.0,
            'scenario': 'election_2024',
            'events': [
                {
                    'date': datetime(2024, 10, 15),
                    'event': 'Debate performance',
                    'volume_spike': 5.2,  # 5.2x normal volume
                    'probability_change': 0.08,  # 8% move
                    'expected_signal': 'volume_spike'
                },
                {
                    'date': datetime(2024, 11, 1),
                    'event': 'Early voting data leak',
                    'volume_spike': 8.5,  # 8.5x normal volume
                    'probability_change': 0.12,  # 12% move
                    'expected_signal': 'volume_spike'
                },
                {
                    'date': datetime(2024, 11, 4),
                    'event': 'Election night',
                    'volume_spike': 15.0,  # 15x normal volume
                    'probability_change': 0.25,  # 25% move
                    'expected_signal': 'volume_spike'
                }
            ]
        }
    
    @staticmethod
    def create_crypto_crash_scenario() -> Dict[str, Any]:
        """Create simulated crypto market crash scenario."""
        return {
            'market_id': 'crypto_crash_sim',
            'question': 'Will Bitcoin drop below $40,000 by end of 2024?',
            'category': 'crypto',
            'active': True,
            'liquidity': 75000.0,
            'volume': 15000.0,
            'scenario': 'crypto_crash',
            'events': [
                {
                    'date': datetime(2024, 9, 15),
                    'event': 'Regulatory news',
                    'volume_spike': 6.0,
                    'probability_change': 0.15,
                    'expected_signal': 'volume_spike'
                },
                {
                    'date': datetime(2024, 10, 1),
                    'event': 'Large whale movement',
                    'volume_spike': 4.5,
                    'unusual_trades': [
                        {'size': 5000, 'price': 0.65, 'value': 3250}
                    ],
                    'expected_signal': 'unusual_trade_size'
                }
            ]
        }
    
    @staticmethod
    def create_taiwan_invasion_scenario() -> Dict[str, Any]:
        """Create simulated Taiwan invasion scenario (based on real tweet example).
        
        Real event: A fresh Polymarket account made a $300K bet that China will 
        invade Taiwan in 2025. The wallet was ~24 hours old, single large bet.
        """
        return {
            'market_id': 'taiwan_invasion_sim',
            'question': 'Will China invade Taiwan in 2025?',
            'category': 'politics',
            'active': True,
            'liquidity': 500000.0,  # High liquidity market
            'volume': 50000.0,  # High volume
            'base_probability': 0.15,  # Low probability (15%) - high payout if correct
            'scenario': 'taiwan_invasion',
            'events': [
                {
                    'date': datetime(2025, 1, 5, 12, 0),  # Jan 5, 2025 at noon
                    'event': 'Fresh wallet $300K bet on Taiwan invasion',
                    'volume_spike': 2.5,  # Volume spike from the large bet
                    'fresh_wallet_bet': {
                        'wallet_age_hours': 24,  # Fresh account (~1 day old)
                        'bet_size_usd': 300000,  # $300K bet (matches tweet)
                        'total_trades': 1,  # Single trade (first bet)
                        'allocation_pct': 100.0  # 100% allocation to this market
                    },
                    'expected_signal': 'fresh_wallet_large_bet'
                }
            ]
        }
    
    @staticmethod
    def create_sports_championship_scenario() -> Dict[str, Any]:
        """Create simulated sports championship scenario."""
        return {
            'market_id': 'sports_championship_sim',
            'question': 'Will the Chiefs win Super Bowl 2025?',
            'category': 'sports',
            'active': True,
            'liquidity': 30000.0,
            'volume': 8000.0,
            'scenario': 'sports_championship',
            'events': [
                {
                    'date': datetime(2024, 12, 15),
                    'event': 'Playoff performance',
                    'volume_spike': 3.8,
                    'probability_change': 0.10,
                    'expected_signal': 'volume_spike'
                }
            ]
        }
    
    @staticmethod
    def generate_historical_market_data(
        market: Dict[str, Any],
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Generate historical market data points.
        
        Args:
            market: Market configuration
            days_back: How many days of history to generate
            
        Returns:
            List of historical data points
        """
        base_volume = market.get('volume', 1000.0)
        base_prob = 0.5
        history = []
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(days_back * 24):  # Hourly data points
            timestamp = start_date + timedelta(hours=i)
            
            # Base volume with some randomness
            volume = base_volume * (0.8 + random.random() * 0.4)
            prob = base_prob + (random.random() - 0.5) * 0.1
            
            # Check for events
            for event in market.get('events', []):
                hours_diff = (timestamp - event['date']).total_seconds() / 3600
                if 0 <= hours_diff < 4:  # Event happening
                    volume = base_volume * event.get('volume_spike', 1.0)
                    prob = base_prob + event.get('probability_change', 0.0)
                    break
            
            history.append({
                'timestamp': timestamp,
                'volume_24h': volume,
                'probability': max(0.0, min(1.0, prob))
            })
        
        return history
    
    @staticmethod
    def generate_historical_trades(
        market: Dict[str, Any],
        event_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate historical trades around an event.
        
        Args:
            market: Market configuration
            event_date: Date of the event
            
        Returns:
            List of trade dictionaries
        """
        trades = []
        
        # Generate normal trades
        for i in range(20):
            trades.append({
                'trader_address': f'0x{random.randint(1000, 9999)}',
                'size': random.randint(10, 100),
                'price': 0.5 + (random.random() - 0.5) * 0.1,
                'timestamp': event_date - timedelta(hours=random.randint(1, 24))
            })
        
        # Add event-specific trades
        for event in market.get('events', []):
            if 'unusual_trades' in event:
                for trade in event['unusual_trades']:
                    trades.append({
                        'trader_address': f'0x{random.randint(1000, 9999)}',
                        'size': trade['size'],
                        'price': trade['price'],
                        'timestamp': event['date']
                    })
        
        return trades
