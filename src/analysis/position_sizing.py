"""Position sizing using Kelly Criterion and risk management."""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """Calculate optimal position sizes using Kelly Criterion."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize position sizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.bankroll = config.get('bankroll_size_usd', 10000)
        self.kelly_fraction = config.get('kelly_fraction', 0.5)
        self.max_exposure_pct = config.get('max_exposure_pct', 40)
    
    def calculate_kelly_size(
        self,
        market_prob: float,
        fair_prob: float,
        bankroll: Optional[float] = None
    ) -> float:
        """Calculate position size using Kelly Criterion.
        
        Args:
            market_prob: Market probability (0-1)
            fair_prob: Your estimated fair probability (0-1)
            bankroll: Bankroll size (uses config default if None)
            
        Returns:
            Position size in USD
        """
        if bankroll is None:
            bankroll = self.bankroll
        
        if market_prob <= 0 or market_prob >= 1:
            return 0.0
        
        if fair_prob <= 0 or fair_prob >= 1:
            return 0.0
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds (1/prob - 1), p = win prob (fair_prob), q = loss prob (1 - fair_prob)
        odds = (1 / market_prob) - 1
        win_prob = fair_prob
        loss_prob = 1 - fair_prob
        
        if odds <= 0:
            return 0.0
        
        kelly_fraction = (odds * win_prob - loss_prob) / odds
        
        # Apply fractional Kelly (typically 0.25 to 0.5)
        kelly_fraction *= self.kelly_fraction
        
        # Ensure non-negative
        kelly_fraction = max(0, kelly_fraction)
        
        # Cap at maximum exposure
        max_size = bankroll * (self.max_exposure_pct / 100)
        position_size = min(kelly_fraction * bankroll, max_size)
        
        return position_size
    
    def adjust_for_correlation(
        self,
        base_size: float,
        correlation: float,
        existing_exposure: float
    ) -> float:
        """Adjust position size based on correlation with existing positions.
        
        Args:
            base_size: Base position size from Kelly
            correlation: Correlation coefficient with existing positions
            existing_exposure: Current total exposure in USD
            
        Returns:
            Adjusted position size
        """
        correlation_threshold = self.config.get('correlation_threshold', 0.7)
        reduction_factor = self.config.get('correlation_reduction_factor', 0.5)
        
        if abs(correlation) >= correlation_threshold:
            # Reduce size if highly correlated
            adjusted_size = base_size * reduction_factor
        else:
            adjusted_size = base_size
        
        # Check total exposure limit
        max_exposure = self.bankroll * (self.max_exposure_pct / 100)
        if existing_exposure + adjusted_size > max_exposure:
            adjusted_size = max(0, max_exposure - existing_exposure)
        
        return adjusted_size
    
    def calculate_position_size(
        self,
        market_prob: float,
        fair_prob: float,
        correlation: float = 0.0,
        existing_exposure: float = 0.0
    ) -> Dict[str, Any]:
        """Calculate final position size with all adjustments.
        
        Args:
            market_prob: Market probability (0-1)
            fair_prob: Estimated fair probability (0-1)
            correlation: Correlation with existing positions
            existing_exposure: Current total exposure
            
        Returns:
            Dictionary with position sizing details
        """
        kelly_size = self.calculate_kelly_size(market_prob, fair_prob)
        adjusted_size = self.adjust_for_correlation(kelly_size, correlation, existing_exposure)
        
        edge = fair_prob - market_prob
        
        return {
            'kelly_size': kelly_size,
            'adjusted_size': adjusted_size,
            'edge': edge,
            'edge_pct': edge * 100,
            'bankroll_pct': (adjusted_size / self.bankroll) * 100 if self.bankroll > 0 else 0
        }
