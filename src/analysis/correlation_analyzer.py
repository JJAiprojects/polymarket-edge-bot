"""Correlation analysis between markets."""
from typing import Dict, Any, List, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """Analyze correlations between markets."""
    
    def __init__(self, database):
        """Initialize correlation analyzer.
        
        Args:
            database: Database instance
        """
        self.db = database
    
    def calculate_correlation(
        self,
        market1_id: str,
        market2_id: str,
        days: int = 7
    ) -> float:
        """Calculate correlation coefficient between two markets.
        
        Args:
            market1_id: First market ID
            market2_id: Second market ID
            days: Number of days to analyze
        
        Returns:
            Correlation coefficient (-1 to 1)
        """
        # Get historical probabilities
        from datetime import timedelta
        hours = days * 24
        
        hist1 = self.db.get_market_volume_history(market1_id, hours=hours)
        hist2 = self.db.get_market_volume_history(market2_id, hours=hours)
        
        if len(hist1) < 2 or len(hist2) < 2:
            return 0.0
        
        # Align timestamps and extract probabilities
        # Create a mapping by timestamp
        hist1_dict = {h['timestamp']: h['probability'] for h in hist1}
        hist2_dict = {h['timestamp']: h['probability'] for h in hist2}
        
        # Find common timestamps
        common_times = set(hist1_dict.keys()) & set(hist2_dict.keys())
        
        if len(common_times) < 2:
            return 0.0
        
        # Extract aligned probabilities
        probs1 = [hist1_dict[t] for t in sorted(common_times)]
        probs2 = [hist2_dict[t] for t in sorted(common_times)]
        
        # Calculate correlation
        try:
            correlation = np.corrcoef(probs1, probs2)[0, 1]
            if np.isnan(correlation):
                return 0.0
            return float(correlation)
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def find_correlated_markets(
        self,
        market_id: str,
        threshold: float = 0.7,
        days: int = 7
    ) -> List[Tuple[str, float]]:
        """Find markets correlated with a given market.
        
        Args:
            market_id: Market ID to find correlations for
            threshold: Minimum correlation threshold
            days: Number of days to analyze
            
        Returns:
            List of tuples (market_id, correlation)
        """
        # This would require getting all markets from database
        # For now, return empty list - can be expanded
        correlated = []
        
        # In a full implementation, we'd:
        # 1. Get all active markets from database
        # 2. Calculate correlation with each
        # 3. Return those above threshold
        
        return correlated
    
    def check_correlation_divergence(
        self,
        market1_id: str,
        market2_id: str,
        market1_current_prob: float,
        market2_current_prob: float,
        threshold: float = 0.7,
        movement_delta: float = 5.0
    ) -> Dict[str, Any]:
        """Check if correlated markets have diverged.
        
        Args:
            market1_id: First market ID
            market2_id: Second market ID
            market1_current_prob: Current probability of market 1
            market2_current_prob: Current probability of market 2
            threshold: Correlation threshold
            movement_delta: Minimum movement percentage
            
        Returns:
            Dictionary with divergence analysis
        """
        correlation = self.calculate_correlation(market1_id, market2_id)
        
        hist1 = self.db.get_market_volume_history(market1_id, hours=24)
        hist2 = self.db.get_market_volume_history(market2_id, hours=24)
        
        if len(hist1) < 2 or len(hist2) < 2:
            return {
                'correlated': False,
                'diverged': False,
                'correlation': correlation
            }
        
        prev_prob1 = hist1[-2]['probability']
        prev_prob2 = hist2[-2]['probability']
        
        movement1 = abs(market1_current_prob - prev_prob1) * 100
        movement2 = abs(market2_current_prob - prev_prob2) * 100
        
        is_correlated = abs(correlation) >= threshold
        has_diverged = False
        
        if is_correlated:
            # Check if one moved significantly more than the other
            if movement1 >= movement_delta and movement2 < movement_delta * 0.5:
                has_diverged = True
            elif movement2 >= movement_delta and movement1 < movement_delta * 0.5:
                has_diverged = True
        
        return {
            'correlated': is_correlated,
            'diverged': has_diverged,
            'correlation': correlation,
            'market1_movement_pct': movement1,
            'market2_movement_pct': movement2
        }
