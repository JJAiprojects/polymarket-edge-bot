"""Twitter monitoring for early signals."""
import tweepy
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class TwitterMonitor:
    """Monitor Twitter for market-related signals."""
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize Twitter monitor.
        
        Args:
            bearer_token: Twitter API v2 bearer token
        """
        self.bearer_token = bearer_token
        self.client = None
        
        if bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
    
    def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        hours_back: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for tweets matching query.
        
        Args:
            query: Search query (supports Twitter search syntax)
            max_results: Maximum number of results (max 100)
            hours_back: How many hours back to search
            
        Returns:
            List of tweet data dictionaries
        """
        if not self.client:
            logger.debug("Twitter client not initialized")
            return []
        
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time_str,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweets.data:
                return []
            
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    def search_market_keywords(
        self,
        keywords: List[str],
        hours_back: int = 1
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search for tweets containing market-related keywords.
        
        Args:
            keywords: List of keywords to search for
            hours_back: How many hours back to search
            
        Returns:
            Dictionary mapping keyword to list of tweets
        """
        results = {}
        
        for keyword in keywords:
            query = f"{keyword} -is:retweet lang:en"
            tweets = self.search_tweets(query, max_results=100, hours_back=hours_back)
            results[keyword] = tweets
        
        return results
    
    def count_mentions(
        self,
        keywords: List[str],
        hours_back: int = 1
    ) -> Dict[str, int]:
        """Count mentions of keywords in recent tweets.
        
        Args:
            keywords: List of keywords to count
            hours_back: How many hours back to search
            
        Returns:
            Dictionary mapping keyword to mention count
        """
        counts = {}
        search_results = self.search_market_keywords(keywords, hours_back=hours_back)
        
        for keyword, tweets in search_results.items():
            counts[keyword] = len(tweets)
        
        return counts
    
    def detect_signal(
        self,
        market_topic: str,
        min_mentions: int = 15,
        hours_back: int = 1
    ) -> bool:
        """Detect if there's a signal based on mention count.
        
        Args:
            market_topic: Topic/keyword to search for
            min_mentions: Minimum mentions to trigger signal
            hours_back: How many hours back to search
            
        Returns:
            True if signal detected
        """
        counts = self.count_mentions([market_topic], hours_back=hours_back)
        mention_count = counts.get(market_topic, 0)
        
        return mention_count >= min_mentions
