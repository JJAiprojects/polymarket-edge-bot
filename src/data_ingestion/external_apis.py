"""External API integrations (Manifold, Metaculus, etc.)."""
import requests
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ExternalAPIs:
    """Client for external prediction market APIs."""
    
    def __init__(self, manifold_api_key: Optional[str] = None, metaculus_api_key: Optional[str] = None):
        """Initialize external API clients.
        
        Args:
            manifold_api_key: Optional Manifold Markets API key
            metaculus_api_key: Optional Metaculus API key
        """
        self.manifold_api_key = manifold_api_key
        self.metaculus_api_key = metaculus_api_key
        self.manifold_base = "https://api.manifold.markets/v0"
        self.metaculus_base = "https://www.metaculus.com/api2"
    
    def search_manifold_market(self, question: str) -> Optional[Dict[str, Any]]:
        """Search for similar market on Manifold.
        
        Args:
            question: Market question text
            
        Returns:
            Market data if found, None otherwise
        """
        if not self.manifold_api_key:
            logger.debug("Manifold API key not provided")
            return None
        
        try:
            # Simple search - Manifold API may require different approach
            # This is a placeholder for actual implementation
            params = {
                'text': question[:100],  # Truncate for search
                'limit': 1
            }
            
            headers = {}
            if self.manifold_api_key:
                headers['Authorization'] = f'Key {self.manifold_api_key}'
            
            response = requests.get(
                f"{self.manifold_base}/search-markets",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return data[0]
            
            return None
        except Exception as e:
            logger.error(f"Error searching Manifold: {e}")
            return None
    
    def get_manifold_probability(self, question: str) -> Optional[float]:
        """Get probability from Manifold for similar question.
        
        Args:
            question: Market question text
            
        Returns:
            Probability (0-1) if found, None otherwise
        """
        market = self.search_manifold_market(question)
        if market and 'probability' in market:
            return float(market['probability'])
        return None
    
    def get_metaculus_probability(self, question: str) -> Optional[float]:
        """Get probability from Metaculus (placeholder - requires API access).
        
        Args:
            question: Market question text
            
        Returns:
            Probability (0-1) if found, None otherwise
        """
        if not self.metaculus_api_key:
            logger.debug("Metaculus API key not provided")
            return None
        
        # Metaculus API implementation would go here
        # This is a placeholder
        logger.debug("Metaculus API not yet implemented")
        return None
    
    def compare_probabilities(
        self,
        polymarket_prob: float,
        question: str
    ) -> Dict[str, Any]:
        """Compare Polymarket probability with external sources.
        
        Args:
            polymarket_prob: Polymarket probability (0-1)
            question: Market question text
            
        Returns:
            Dictionary with comparison data
        """
        result = {
            'polymarket_prob': polymarket_prob,
            'manifold_prob': None,
            'metaculus_prob': None,
            'divergences': {}
        }
        
        manifold_prob = self.get_manifold_probability(question)
        if manifold_prob is not None:
            result['manifold_prob'] = manifold_prob
            divergence = abs(polymarket_prob - manifold_prob) * 100
            result['divergences']['manifold'] = divergence
        
        metaculus_prob = self.get_metaculus_probability(question)
        if metaculus_prob is not None:
            result['metaculus_prob'] = metaculus_prob
            divergence = abs(polymarket_prob - metaculus_prob) * 100
            result['divergences']['metaculus'] = divergence
        
        return result
