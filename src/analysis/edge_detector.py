"""Edge detection logic for identifying opportunities."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class EdgeDetector:
    """Detects edges and opportunities in markets."""
    
    def __init__(self, config: Dict[str, Any], database):
        """Initialize edge detector.
        
        Args:
            config: Configuration dictionary
            database: Database instance
        """
        self.config = config
        self.db = database
    
    def detect_volume_spike(
        self,
        market_id: str,
        current_volume: float,
        hours: int = 4
    ) -> Optional[Dict[str, Any]]:
        """Detect volume spike in a market.
        
        Args:
            market_id: Market ID
            current_volume: Current volume over time window
            hours: Time window in hours
            
        Returns:
            Signal dictionary if spike detected, None otherwise
        """
        multiplier = self.config.get('volume_spike_multiplier', 4.0)
        
        # Get historical volume data
        history = self.db.get_market_volume_history(market_id, hours=24)
        
        if len(history) < 2:
            return None
        
        # Calculate average volume over historical period
        avg_volume = sum(h['volume_24h'] for h in history) / len(history)
        
        if avg_volume == 0:
            return None
        
        spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if spike_ratio >= multiplier:
            return {
                'type': 'volume_spike',
                'market_id': market_id,
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'spike_ratio': spike_ratio,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
    
    def detect_smart_wallet_activity(
        self,
        trades: List[Dict[str, Any]],
        wallet_success_rate: float,
        min_trades: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Detect activity from smart wallets.
        
        Args:
            trades: List of recent trades
            wallet_success_rate: Success rate threshold
            min_trades: Minimum trades to qualify
            
        Returns:
            Signal dictionary if smart wallet detected, None otherwise
        """
        # Group trades by wallet
        wallet_trades = {}
        for trade in trades:
            wallet = trade.get('trader_address')
            if wallet:
                if wallet not in wallet_trades:
                    wallet_trades[wallet] = []
                wallet_trades[wallet].append(trade)
        
        # Check for smart wallets
        smart_wallets = []
        for wallet, wallet_trade_list in wallet_trades.items():
            if len(wallet_trade_list) >= min_trades:
                # In a real implementation, we'd check historical P&L
                # For now, flag wallets with high trade frequency
                from src.database import Wallet
                session = self.db.get_session()
                try:
                    wallet_record = session.query(Wallet).filter_by(address=wallet).first()
                    if wallet_record and wallet_record.success_rate >= wallet_success_rate:
                        smart_wallets.append({
                            'address': wallet,
                            'success_rate': wallet_record.success_rate,
                            'total_trades': wallet_record.total_trades,
                            'recent_trades': len(wallet_trade_list)
                        })
                finally:
                    session.close()
        
        if smart_wallets:
            return {
                'type': 'smart_wallet',
                'wallets': smart_wallets,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
    
    def detect_probability_divergence(
        self,
        polymarket_prob: float,
        external_probs: Dict[str, float],
        threshold_pct: float = 12.0
    ) -> Optional[Dict[str, Any]]:
        """Detect divergence between Polymarket and external probabilities.
        
        Args:
            polymarket_prob: Polymarket probability (0-1)
            external_probs: Dictionary of external probabilities
            threshold_pct: Divergence threshold percentage
            
        Returns:
            Signal dictionary if divergence detected, None otherwise
        """
        divergences = {}
        
        for source, prob in external_probs.items():
            if prob is not None:
                divergence_pct = abs(polymarket_prob - prob) * 100
                if divergence_pct >= threshold_pct:
                    divergences[source] = {
                        'polymarket_prob': polymarket_prob,
                        'external_prob': prob,
                        'divergence_pct': divergence_pct
                    }
        
        if divergences:
            return {
                'type': 'probability_divergence',
                'divergences': divergences,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
    
    def detect_twitter_signal(
        self,
        market_topic: str,
        mention_count: int,
        min_mentions: int = 15
    ) -> Optional[Dict[str, Any]]:
        """Detect Twitter signal for a market.
        
        Args:
            market_topic: Market topic/keyword
            mention_count: Number of mentions
            min_mentions: Minimum mentions threshold
            
        Returns:
            Signal dictionary if signal detected, None otherwise
        """
        if mention_count >= min_mentions:
            return {
                'type': 'twitter_signal',
                'topic': market_topic,
                'mention_count': mention_count,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
    
    def detect_correlation_divergence(
        self,
        market1_id: str,
        market2_id: str,
        market1_prob: float,
        market2_prob: float,
        historical_correlation: float,
        threshold: float = 0.7,
        movement_delta: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """Detect when correlated markets diverge.
        
        Args:
            market1_id: First market ID
            market2_id: Second market ID
            market1_prob: Current probability of market 1
            market2_prob: Current probability of market 2
            historical_correlation: Historical correlation coefficient
            threshold: Minimum correlation to consider
            movement_delta: Minimum movement percentage to flag
            
        Returns:
            Signal dictionary if divergence detected, None otherwise
        """
        if abs(historical_correlation) < threshold:
            return None
        
        # Get historical probabilities
        hist1 = self.db.get_market_volume_history(market1_id, hours=24)
        hist2 = self.db.get_market_volume_history(market2_id, hours=24)
        
        if len(hist1) < 2 or len(hist2) < 2:
            return None
        
        # Get previous probabilities
        prev_prob1 = hist1[-2]['probability']
        prev_prob2 = hist2[-2]['probability']
        
        # Calculate movements
        movement1 = abs(market1_prob - prev_prob1) * 100
        movement2 = abs(market2_prob - prev_prob2) * 100
        
        # Check if one moved significantly without the other
        if movement1 >= movement_delta and movement2 < movement_delta * 0.5:
            return {
                'type': 'correlation_divergence',
                'market1_id': market1_id,
                'market2_id': market2_id,
                'market1_movement_pct': movement1,
                'market2_movement_pct': movement2,
                'correlation': historical_correlation,
                'detected_at': datetime.now(timezone.utc)
            }
        
        if movement2 >= movement_delta and movement1 < movement_delta * 0.5:
            return {
                'type': 'correlation_divergence',
                'market1_id': market1_id,
                'market2_id': market2_id,
                'market1_movement_pct': movement1,
                'market2_movement_pct': movement2,
                'correlation': historical_correlation,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
    
    def calculate_expected_value(
        self,
        probability: float,
        fair_probability: float,
        bet_size: float
    ) -> float:
        """Calculate expected value of a bet.
        
        Args:
            probability: Market probability (0-1)
            fair_probability: Your estimated fair probability (0-1)
            bet_size: Bet size in USD
            
        Returns:
            Expected value in USD
        """
        if probability <= 0 or probability >= 1:
            return 0.0
        
        # EV = (fair_probability * (1/prob - 1) - (1 - fair_probability)) * bet_size
        # Simplified: EV = (fair_probability / prob - 1) * bet_size
        ev = (fair_probability / probability - 1) * bet_size
        
        return ev
    
    def detect_unusual_trade_size(
        self,
        trades: List[Dict[str, Any]],
        min_size_usd: float = 1000
    ) -> Optional[Dict[str, Any]]:
        """Detect unusually large trades.
        
        Args:
            trades: List of recent trades
            min_size_usd: Minimum size to flag as unusual
            
        Returns:
            Signal dictionary if unusual trades detected, None otherwise
        """
        unusual_trades = []
        
        for trade in trades:
            size = float(trade.get('size', 0))
            price = float(trade.get('price', 0))
            trade_value = size * price
            
            if trade_value >= min_size_usd:
                unusual_trades.append({
                    'trader_address': trade.get('trader_address'),
                    'size': size,
                    'price': price,
                    'value_usd': trade_value,
                    'timestamp': trade.get('timestamp')
                })
        
        if unusual_trades:
            return {
                'type': 'unusual_trade_size',
                'trades': unusual_trades,
                'detected_at': datetime.now(timezone.utc)
            }
        
        return None
