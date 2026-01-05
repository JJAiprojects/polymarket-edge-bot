"""Polymarket Gamma API client."""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class PolymarketAPI:
    """Client for Polymarket Gamma API."""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self, rate_limit: int = 60):
        """Initialize Polymarket API client.
        
        Args:
            rate_limit: Requests per minute
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.min_interval = 60.0 / rate_limit
    
    def _rate_limit_wait(self):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response data
        """
        self._rate_limit_wait()
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {endpoint} - {e}")
            raise
    
    def get_markets(
        self,
        category: Optional[str] = None,
        active: bool = True,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get active markets.
        
        Args:
            category: Market category filter (e.g., 'politics')
            active: Only return active markets
            limit: Maximum number of results
            
        Returns:
            List of market data dictionaries
        """
        params = {
            'active': str(active).lower(),
            'limit': limit
        }
        if category:
            params['category'] = category
        
        data = self._request('/markets', params=params)
        return data if isinstance(data, list) else data.get('data', [])
    
    def get_market(self, market_id: str) -> Dict[str, Any]:
        """Get specific market details.
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            Market data dictionary
        """
        return self._request(f'/markets/{market_id}')
    
    def get_trades(
        self,
        market_id: Optional[str] = None,
        limit: int = 100,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get recent trades.
        
        Args:
            market_id: Filter by market ID
            limit: Maximum number of results
            start_time: Only return trades after this time
            
        Returns:
            List of trade data dictionaries
        """
        params = {'limit': limit}
        if market_id:
            params['market'] = market_id
        if start_time:
            params['startTime'] = int(start_time.timestamp())
        
        data = self._request('/trades', params=params)
        return data if isinstance(data, list) else data.get('data', [])
    
    def get_orderbook(self, market_id: str) -> Dict[str, Any]:
        """Get order book for a market.
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            Order book data
        """
        return self._request(f'/markets/{market_id}/orderbook')
    
    def get_market_prices(self, market_id: str) -> Dict[str, float]:
        """Get current prices/probabilities for market outcomes.
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            Dictionary mapping outcome to probability
        """
        market = self.get_market(market_id)
        prices = {}
        
        # Extract prices from market data
        if 'tokens' in market:
            for token in market['tokens']:
                outcome = token.get('outcome', '')
                price = token.get('price', 0.0)
                prices[outcome] = float(price)
        
        return prices
    
    def get_market_volume(self, market_id: str, hours: int = 24) -> float:
        """Get market volume over specified hours.
        
        Args:
            market_id: Polymarket market ID
            hours: Number of hours to look back
            
        Returns:
            Total volume in USD
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        trades = self.get_trades(market_id=market_id, start_time=start_time)
        
        total_volume = 0.0
        for trade in trades:
            # Calculate volume: size * price
            size = float(trade.get('size', 0))
            price = float(trade.get('price', 0))
            total_volume += size * price
        
        return total_volume
