"""Database layer for storing historical data and trade journal."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

Base = declarative_base()


class Market(Base):
    """Market data table."""
    __tablename__ = 'markets'
    
    id = Column(String, primary_key=True)  # Polymarket market ID
    question = Column(String, nullable=False)
    category = Column(String)
    resolution_date = Column(DateTime)
    current_probability = Column(Float)
    volume_24h = Column(Float)
    liquidity = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Trade(Base):
    """Trade data table."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String, nullable=False, index=True)
    trader_address = Column(String, nullable=False, index=True)
    side = Column(String)  # 'buy' or 'sell'
    size = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Wallet(Base):
    """Wallet tracking table."""
    __tablename__ = 'wallets'
    
    address = Column(String, primary_key=True)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    total_volume_usd = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class FlaggedOpportunity(Base):
    """Flagged opportunities/journal table."""
    __tablename__ = 'flagged_opportunities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String, nullable=False, index=True)
    market_question = Column(String)
    signal_type = Column(String)  # 'volume_spike', 'divergence', 'smart_wallet', etc.
    current_probability = Column(Float)
    expected_value = Column(Float)
    suggested_size_usd = Column(Float)
    rationale = Column(Text)
    metadata_json = Column(Text)  # JSON string for additional data
    flagged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved = Column(Boolean, default=False)
    outcome = Column(String)  # 'win', 'loss', 'pending'
    pnl = Column(Float)


class HistoricalProbability(Base):
    """Historical probability tracking."""
    __tablename__ = 'historical_probabilities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String, nullable=False, index=True)
    probability = Column(Float)
    volume_24h = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Database:
    """Database manager."""
    
    def __init__(self, db_path: str = "data/bot_data.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.Session()
    
    def add_market(self, market_data: Dict[str, Any]) -> None:
        """Add or update market data."""
        session = self.get_session()
        try:
            market = session.query(Market).filter_by(id=market_data['id']).first()
            if market:
                for key, value in market_data.items():
                    if key != 'id':
                        setattr(market, key, value)
                market.updated_at = datetime.now(timezone.utc)
            else:
                market = Market(**market_data)
                session.add(market)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_trade(self, trade_data: Dict[str, Any]) -> None:
        """Add trade data."""
        session = self.get_session()
        try:
            trade = Trade(**trade_data)
            session.add(trade)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_historical_probability(self, market_id: str, probability: float, volume_24h: float) -> None:
        """Add historical probability snapshot."""
        session = self.get_session()
        try:
            hist = HistoricalProbability(
                market_id=market_id,
                probability=probability,
                volume_24h=volume_24h
            )
            session.add(hist)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_market_volume_history(self, market_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get volume history for a market."""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            results = session.query(HistoricalProbability).filter(
                HistoricalProbability.market_id == market_id,
                HistoricalProbability.timestamp >= cutoff
            ).order_by(HistoricalProbability.timestamp).all()
            
            return [
                {
                    'timestamp': r.timestamp,
                    'volume_24h': r.volume_24h,
                    'probability': r.probability
                }
                for r in results
            ]
        finally:
            session.close()
    
    def flag_opportunity(self, opportunity_data: Dict[str, Any]) -> int:
        """Flag a new opportunity."""
        session = self.get_session()
        try:
            # Convert metadata dict to JSON string and rename key
            db_data = opportunity_data.copy()
            if 'metadata' in db_data:
                if isinstance(db_data['metadata'], dict):
                    db_data['metadata_json'] = json.dumps(db_data['metadata'])
                else:
                    db_data['metadata_json'] = db_data['metadata']
                del db_data['metadata']
            
            opportunity = FlaggedOpportunity(**db_data)
            session.add(opportunity)
            session.commit()
            return opportunity.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
