"""Detect fresh wallet large bet patterns (insider signals)."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class FreshWalletDetector:
    """Detect suspicious patterns from fresh wallets making large bets."""
    
    def __init__(self, config: Dict[str, Any], database, blockchain_monitor):
        """Initialize fresh wallet detector.
        
        Args:
            config: Configuration dictionary
            database: Database instance
            blockchain_monitor: BlockchainMonitor instance
        """
        self.config = config
        self.db = database
        self.blockchain = blockchain_monitor
        
        self.wallet_age_hours = config.get('fresh_wallet_age_hours', 72)  # 48-72 hours
        self.min_fresh_wallet_bet_usd = config.get('min_fresh_wallet_bet_usd', 5000)  # $5k-$10k
        self.max_wallet_trades = config.get('fresh_wallet_max_trades', 3)  # <3 trades
        self.min_allocation_pct = config.get('fresh_wallet_min_allocation_pct', 80.0)  # >80% to one outcome
    
    def detect_fresh_wallet_large_bet(
        self,
        market_id: str,
        trades: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Detect if a fresh wallet made a large bet on this market.
        
        Args:
            market_id: Market ID
            trades: List of recent trades for this market
            
        Returns:
            Signal dictionary if detected, None otherwise
        """
        if not trades:
            return None
        
        # Group trades by wallet
        wallet_trades = {}
        for trade in trades:
            wallet = trade.get('trader_address')
            if wallet:
                if wallet not in wallet_trades:
                    wallet_trades[wallet] = []
                wallet_trades[wallet].append(trade)
        
        # Check each wallet
        for wallet, wallet_trade_list in wallet_trades.items():
            # Calculate total bet size for this wallet on this market
            total_bet_value = 0.0
            for trade in wallet_trade_list:
                size = float(trade.get('size', 0))
                price = float(trade.get('price', 0))
                total_bet_value += size * price
            
            # Check if bet is large enough
            if total_bet_value < self.min_fresh_wallet_bet_usd:
                continue
            
            # Check wallet age
            wallet_age = self.blockchain.get_wallet_age(wallet)
            if wallet_age is None:
                # If we can't determine age, skip (requires PolygonScan API)
                continue
            
            if wallet_age > self.wallet_age_hours:
                continue  # Wallet too old
            
            # Check total trades across all markets (single-market focus)
            total_trades = len(wallet_trade_list)
            if total_trades > self.max_wallet_trades:
                continue  # Wallet has too many trades (not focused)
            
            # Check if this is wallet's first/largest activity
            # Get all trades for this wallet from database
            session = self.db.get_session()
            try:
                from src.database import Trade
                all_wallet_trades = session.query(Trade).filter_by(
                    trader_address=wallet
                ).all()
                
                # Count trades on this specific market vs all markets
                market_trades = [t for t in all_wallet_trades if t.market_id == market_id]
                total_trades_count = len(all_wallet_trades)
                
                # If wallet has too many total trades, skip (not focused enough)
                if total_trades_count > self.max_wallet_trades:
                    continue
                
                # Check allocation concentration
                # Calculate what % of wallet's total activity is on this market
                total_wallet_activity = sum(
                    float(t.size or 0) * float(t.price or 0) 
                    for t in all_wallet_trades
                ) if all_wallet_trades else total_bet_value
                
                if total_wallet_activity > 0:
                    allocation_pct = (total_bet_value / total_wallet_activity) * 100
                else:
                    allocation_pct = 100.0  # This is wallet's only activity
                
                if allocation_pct < self.min_allocation_pct:
                    continue  # Not concentrated enough
                
                # Check if this appears to be wallet's first major activity
                # (no prior large trades on other markets)
                has_prior_large_trades = any(
                    float(t.size or 0) * float(t.price or 0) >= self.min_fresh_wallet_bet_usd
                    for t in all_wallet_trades
                    if t.market_id != market_id
                )
                
                if has_prior_large_trades:
                    continue  # Wallet has made large bets before on other markets
                
                # All checks passed! Return signal
                return {
                    'type': 'fresh_wallet_large_bet',
                    'market_id': market_id,
                    'wallet_address': wallet,
                    'wallet_age_hours': wallet_age,
                    'bet_size_usd': total_bet_value,
                    'total_trades': total_trades_count,
                    'allocation_pct': allocation_pct,
                    'detected_at': datetime.now(timezone.utc)
                }
                
            except Exception as e:
                logger.debug(f"Error checking wallet history: {e}")
                continue
            finally:
                session.close()
        
        return None
    
    def analyze_wallet_pattern(
        self,
        wallet_address: str,
        market_id: str
    ) -> Dict[str, Any]:
        """Analyze a wallet's pattern for insider signals.
        
        Args:
            wallet_address: Wallet address to analyze
            market_id: Market ID
            
        Returns:
            Analysis dictionary
        """
        wallet_age = self.blockchain.get_wallet_age(wallet_address)
        
        session = self.db.get_session()
        try:
            from src.database import Trade
            wallet_trades = session.query(Trade).filter_by(
                trader_address=wallet_address
            ).all()
            
            # Calculate statistics
            total_trades = len(wallet_trades)
            total_volume = sum(
                float(t.size or 0) * float(t.price or 0) 
                for t in wallet_trades
            )
            
            # Market-specific trades
            market_trades = [t for t in wallet_trades if t.market_id == market_id]
            market_volume = sum(
                float(t.size or 0) * float(t.price or 0) 
                for t in market_trades
            )
            
            allocation_pct = (market_volume / total_volume * 100) if total_volume > 0 else 0
            
            return {
                'wallet_address': wallet_address,
                'wallet_age_hours': wallet_age,
                'total_trades': total_trades,
                'total_volume_usd': total_volume,
                'market_trades': len(market_trades),
                'market_volume_usd': market_volume,
                'allocation_pct': allocation_pct,
                'is_fresh': wallet_age is not None and wallet_age <= self.wallet_age_hours,
                'is_focused': total_trades <= self.max_wallet_trades and allocation_pct >= self.min_allocation_pct,
                'has_large_bet': market_volume >= self.min_fresh_wallet_bet_usd
            }
        finally:
            session.close()
