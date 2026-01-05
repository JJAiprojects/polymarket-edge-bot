"""Risk management and portfolio tracking."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk and portfolio constraints."""
    
    def __init__(self, config: Dict[str, Any], database):
        """Initialize risk manager.
        
        Args:
            config: Configuration dictionary
            database: Database instance
        """
        self.config = config
        self.db = database
        self.max_positions = config.get('max_open_positions', 10)
        self.max_exposure_pct = config.get('max_exposure_pct', 40)
        self.bankroll = config.get('bankroll_size_usd', 10000)
    
    def get_current_exposure(self) -> float:
        """Get current total exposure across all positions.
        
        Returns:
            Total exposure in USD
        """
        from src.database import FlaggedOpportunity
        session = self.db.get_session()
        try:
            # Get unresolved flagged opportunities
            positions = session.query(FlaggedOpportunity).filter_by(resolved=False).all()
            total_exposure = sum(pos.suggested_size_usd for pos in positions if pos.suggested_size_usd)
            return total_exposure
        finally:
            session.close()
    
    def get_open_positions_count(self) -> int:
        """Get count of open positions.
        
        Returns:
            Number of open positions
        """
        from src.database import FlaggedOpportunity
        session = self.db.get_session()
        try:
            count = session.query(FlaggedOpportunity).filter_by(resolved=False).count()
            return count
        finally:
            session.close()
    
    def can_take_position(self, position_size: float) -> tuple[bool, Optional[str]]:
        """Check if a new position can be taken.
        
        Args:
            position_size: Proposed position size in USD
            
        Returns:
            Tuple of (can_take, reason_if_no)
        """
        current_exposure = self.get_current_exposure()
        open_positions = self.get_open_positions_count()
        
        # Check position count limit
        if open_positions >= self.max_positions:
            return False, f"Maximum positions limit reached ({self.max_positions})"
        
        # Check exposure limit
        max_exposure = self.bankroll * (self.max_exposure_pct / 100)
        if current_exposure + position_size > max_exposure:
            return False, f"Exposure limit would be exceeded ({current_exposure + position_size:.2f} > {max_exposure:.2f})"
        
        return True, None
    
    def should_hedge(
        self,
        position_prob: float,
        hedge_threshold: float = 0.70
    ) -> bool:
        """Determine if a position should be hedged.
        
        Args:
            position_prob: Current probability of position
            hedge_threshold: Probability threshold for hedging
            
        Returns:
            True if should hedge
        """
        return position_prob >= hedge_threshold
    
    def calculate_hedge_size(
        self,
        position_size: float,
        position_prob: float,
        hedge_prob: float,
        max_hedge_pct: float = 20.0
    ) -> float:
        """Calculate hedge position size.
        
        Args:
            position_size: Original position size
            position_prob: Probability of original position
            hedge_prob: Probability of hedge outcome
            max_hedge_pct: Maximum hedge as percentage of position
            
        Returns:
            Hedge size in USD
        """
        if not self.should_hedge(position_prob):
            return 0.0
        
        # Simple hedge: buy opposing outcome
        # Size based on probability difference
        hedge_size = position_size * (max_hedge_pct / 100)
        
        return hedge_size
    
    def check_stop_loss(
        self,
        market_id: str,
        original_prob: float,
        current_prob: float,
        threshold_pct: float = 20.0
    ) -> bool:
        """Check if stop loss should trigger.
        
        Args:
            market_id: Market ID
            original_prob: Original probability when position opened
            current_prob: Current probability
            threshold_pct: Percentage drop threshold
            
        Returns:
            True if stop loss should trigger
        """
        if original_prob <= 0:
            return False
        
        drop_pct = ((original_prob - current_prob) / original_prob) * 100
        return drop_pct >= threshold_pct
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of current portfolio.
        
        Returns:
            Portfolio summary dictionary
        """
        current_exposure = self.get_current_exposure()
        open_positions = self.get_open_positions_count()
        exposure_pct = (current_exposure / self.bankroll) * 100 if self.bankroll > 0 else 0
        
        return {
            'total_exposure_usd': current_exposure,
            'exposure_pct': exposure_pct,
            'open_positions': open_positions,
            'max_positions': self.max_positions,
            'max_exposure_pct': self.max_exposure_pct,
            'bankroll_usd': self.bankroll,
            'available_capital_usd': self.bankroll - current_exposure
        }
