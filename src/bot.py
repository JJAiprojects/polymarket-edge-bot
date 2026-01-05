"""Main bot orchestrator."""
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from src.config_manager import ConfigManager
from src.logger_setup import setup_logger
from src.database import Database
from src.data_ingestion import PolymarketAPI, BlockchainMonitor, ExternalAPIs, TwitterMonitor
from src.analysis import EdgeDetector, PositionSizer, RiskManager, CorrelationAnalyzer
from src.notifications import TelegramNotifier, DiscordNotifier


class PolymarketBot:
    """Main bot class that orchestrates all components."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the bot.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Setup logging
        log_level = self.config.get('log_level', 'INFO')
        self.logger = setup_logger('polymarket_bot', log_level)
        
        self.logger.info("Initializing Polymarket Edge Detection Bot...")
        
        # Initialize database
        db_path = self.config.get('database_path', 'data/bot_data.db')
        self.db = Database(db_path)
        self.logger.info(f"Database initialized: {db_path}")
        
        # Initialize data sources
        self.polymarket = PolymarketAPI(
            rate_limit=self.config.get('polymarket_rate_limit', 60)
        )
        
        polygon_rpc = self.config.get('polygon_rpc_url', 'https://polygon-rpc.com')
        polygonscan_key = self.config.get('polygonscan_api_key')
        self.blockchain = BlockchainMonitor(polygon_rpc, polygonscan_key)
        
        self.external_apis = ExternalAPIs(
            manifold_api_key=self.config.get('manifold_api_key'),
            metaculus_api_key=self.config.get('metaculus_api_key')
        )
        
        twitter_token = self.config.get('twitter_bearer_token')
        self.twitter = TwitterMonitor(twitter_token) if twitter_token else None
        
        # Initialize analysis components
        config_dict = self.config.get_all()
        self.edge_detector = EdgeDetector(config_dict, self.db)
        self.position_sizer = PositionSizer(config_dict)
        self.risk_manager = RiskManager(config_dict, self.db)
        self.correlation_analyzer = CorrelationAnalyzer(self.db)
        
        # Initialize notifications
        self.notifiers = []
        
        if self.config.get('telegram_enabled', False):
            telegram_token = self.config.get('telegram_bot_token')
            telegram_chat = self.config.get('telegram_chat_id')
            if telegram_token and telegram_chat:
                self.notifiers.append(TelegramNotifier(telegram_token, telegram_chat))
                self.logger.info("Telegram notifications enabled")
        
        if self.config.get('discord_enabled', False):
            discord_token = self.config.get('discord_bot_token')
            discord_channel = self.config.get('discord_channel_id')
            if discord_token and discord_channel:
                # Note: Discord requires async, would need async wrapper
                self.logger.warning("Discord notifications require async implementation")
        
        self.logger.info("Bot initialization complete")
    
    def analyze_market(self, market: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a single market for opportunities.
        
        Args:
            market: Market data dictionary
            
        Returns:
            List of detected opportunities
        """
        market_id = market.get('id')
        question = market.get('question', '')
        category = market.get('category', '')
        
        if not market_id:
            return []
        
        opportunities = []
        
        try:
            # Get current market data
            current_prices = self.polymarket.get_market_prices(market_id)
            if not current_prices:
                return []
            
            # Get main probability (usually 'Yes' outcome)
            main_prob = max(current_prices.values()) if current_prices else 0.5
            
            # Get volume data
            volume_24h = float(market.get('volume', 0))
            volume_4h = self.polymarket.get_market_volume(market_id, hours=4)
            
            # Store historical probability
            self.db.add_historical_probability(market_id, main_prob, volume_24h)
            
            # Store market data
            self.db.add_market({
                'id': market_id,
                'question': question,
                'category': category,
                'current_probability': main_prob,
                'volume_24h': volume_24h,
                'liquidity': float(market.get('liquidity', 0))
            })
            
            # 1. Check for volume spike
            volume_spike = self.edge_detector.detect_volume_spike(
                market_id, volume_4h, hours=4
            )
            if volume_spike:
                opportunities.append({
                    'market_id': market_id,
                    'market_question': question,
                    'signal_type': 'volume_spike',
                    'current_probability': main_prob,
                    'metadata': volume_spike
                })
            
            # 2. Get recent trades
            trades = self.polymarket.get_trades(market_id=market_id, limit=50)
            
            # Check for unusual trade sizes
            unusual_trades = self.edge_detector.detect_unusual_trade_size(
                trades,
                min_size_usd=self.config.get('min_trade_size_usd', 1000)
            )
            if unusual_trades:
                opportunities.append({
                    'market_id': market_id,
                    'market_question': question,
                    'signal_type': 'unusual_trade_size',
                    'current_probability': main_prob,
                    'metadata': unusual_trades
                })
            
            # 3. Check probability divergence with external sources
            if self.config.get('twitter_enabled', False):
                comparison = self.external_apis.compare_probabilities(main_prob, question)
                if comparison.get('divergences'):
                    divergence_threshold = self.config.get('divergence_threshold_pct', 12.0)
                    for source, div_data in comparison['divergences'].items():
                        if div_data['divergence_pct'] >= divergence_threshold:
                            opportunities.append({
                                'market_id': market_id,
                                'market_question': question,
                                'signal_type': 'probability_divergence',
                                'current_probability': main_prob,
                                'metadata': {
                                    'source': source,
                                    'divergence_pct': div_data['divergence_pct'],
                                    'external_prob': div_data['external_prob']
                                }
                            })
            
            # 4. Check Twitter signals
            if self.twitter:
                keywords = self._extract_keywords(question)
                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    mention_count = self.twitter.count_mentions([keyword], hours_back=1).get(keyword, 0)
                    if mention_count >= self.config.get('twitter_min_mentions', 15):
                        opportunities.append({
                            'market_id': market_id,
                            'market_question': question,
                            'signal_type': 'twitter_signal',
                            'current_probability': main_prob,
                            'metadata': {
                                'keyword': keyword,
                                'mention_count': mention_count
                            }
                        })
            
        except Exception as e:
            self.logger.error(f"Error analyzing market {market_id}: {e}", exc_info=True)
        
        return opportunities
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract keywords from market question for Twitter search.
        
        Args:
            question: Market question text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction - can be enhanced with NLP
        words = question.lower().split()
        # Filter out common words
        stop_words = {'will', 'the', 'a', 'an', 'be', 'is', 'are', 'at', 'in', 'on', 'to', 'for', 'of', 'and', 'or'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:5]  # Return top 5 keywords
    
    def process_opportunities(self, opportunities: List[Dict[str, Any]]) -> None:
        """Process detected opportunities and send notifications.
        
        Args:
            opportunities: List of opportunity dictionaries
        """
        for opp in opportunities:
            try:
                # Calculate position size
                market_prob = opp.get('current_probability', 0.5)
                # Estimate fair probability (simplified - in reality would use more sophisticated model)
                fair_prob = market_prob * 1.1  # Assume 10% edge for now
                
                sizing = self.position_sizer.calculate_position_size(
                    market_prob=market_prob,
                    fair_prob=fair_prob
                )
                
                # Calculate expected value
                ev = self.edge_detector.calculate_expected_value(
                    market_prob, fair_prob, sizing['adjusted_size']
                )
                
                # Check if meets notification threshold
                ev_threshold = self.config.get('notification_threshold_ev', 0.05)
                if ev < ev_threshold:
                    continue
                
                # Check risk constraints
                can_take, reason = self.risk_manager.can_take_position(sizing['adjusted_size'])
                if not can_take:
                    self.logger.debug(f"Skipping opportunity due to risk: {reason}")
                    continue
                
                # Build opportunity record
                opportunity_data = {
                    'market_id': opp['market_id'],
                    'market_question': opp['market_question'],
                    'signal_type': opp['signal_type'],
                    'current_probability': market_prob,
                    'expected_value': ev,
                    'suggested_size_usd': sizing['adjusted_size'],
                    'rationale': self._build_rationale(opp, sizing, ev),
                    'metadata': opp.get('metadata', {})
                }
                
                # Flag in database
                opp_id = self.db.flag_opportunity(opportunity_data)
                self.logger.info(f"Flagged opportunity #{opp_id}: {opp['market_question'][:50]}...")
                
                # Send notifications
                for notifier in self.notifiers:
                    try:
                        if isinstance(notifier, TelegramNotifier):
                            notifier.notify_opportunity(opportunity_data)
                    except Exception as e:
                        self.logger.error(f"Failed to send notification: {e}")
                
            except Exception as e:
                self.logger.error(f"Error processing opportunity: {e}", exc_info=True)
    
    def _build_rationale(self, opp: Dict[str, Any], sizing: Dict[str, Any], ev: float) -> str:
        """Build human-readable rationale for an opportunity.
        
        Args:
            opp: Opportunity dictionary
            sizing: Position sizing dictionary
            ev: Expected value
            
        Returns:
            Rationale string
        """
        signal_type = opp['signal_type'].replace('_', ' ').title()
        rationale = f"Signal detected: {signal_type}.\n"
        
        metadata = opp.get('metadata', {})
        
        if opp['signal_type'] == 'volume_spike':
            spike_ratio = metadata.get('spike_ratio', 0)
            rationale += f"Volume spike detected: {spike_ratio:.1f}x average volume.\n"
        
        elif opp['signal_type'] == 'probability_divergence':
            source = metadata.get('source', 'external')
            divergence = metadata.get('divergence_pct', 0)
            rationale += f"Probability divergence with {source}: {divergence:.1f}%.\n"
        
        elif opp['signal_type'] == 'twitter_signal':
            mentions = metadata.get('mention_count', 0)
            keyword = metadata.get('keyword', '')
            rationale += f"Twitter activity spike: {mentions} mentions of '{keyword}'.\n"
        
        rationale += f"Edge: {sizing['edge_pct']:.2f}%. "
        rationale += f"Expected Value: ${ev:.2f}. "
        rationale += f"Suggested position: ${sizing['adjusted_size']:.2f} ({sizing['bankroll_pct']:.1f}% of bankroll)."
        
        return rationale
    
    def run_analysis_cycle(self) -> None:
        """Run a single analysis cycle."""
        self.logger.info("Starting analysis cycle...")
        
        try:
            # Get markets to monitor
            categories = self.config.get('monitor_categories', ['politics'])
            all_markets = []
            
            for category in categories:
                try:
                    markets = self.polymarket.get_markets(category=category, active=True, limit=50)
                    all_markets.extend(markets)
                    self.logger.debug(f"Fetched {len(markets)} markets in category '{category}'")
                except Exception as e:
                    self.logger.error(f"Error fetching markets for category {category}: {e}")
            
            # Filter by liquidity
            min_liquidity = self.config.get('min_liquidity_usd', 5000)
            filtered_markets = [
                m for m in all_markets
                if float(m.get('liquidity', 0)) >= min_liquidity
            ]
            
            self.logger.info(f"Analyzing {len(filtered_markets)} markets...")
            
            # Analyze each market
            all_opportunities = []
            for market in filtered_markets:
                try:
                    opportunities = self.analyze_market(market)
                    all_opportunities.extend(opportunities)
                except Exception as e:
                    self.logger.error(f"Error analyzing market {market.get('id')}: {e}")
            
            # Process opportunities
            if all_opportunities:
                self.logger.info(f"Found {len(all_opportunities)} opportunities")
                self.process_opportunities(all_opportunities)
            else:
                self.logger.info("No opportunities detected in this cycle")
            
            # Log portfolio summary
            portfolio = self.risk_manager.get_portfolio_summary()
            self.logger.info(
                f"Portfolio: {portfolio['open_positions']} positions, "
                f"${portfolio['total_exposure_usd']:.2f} exposure "
                f"({portfolio['exposure_pct']:.1f}%)"
            )
            
        except Exception as e:
            self.logger.error(f"Error in analysis cycle: {e}", exc_info=True)
        
        self.logger.info("Analysis cycle complete")
    
    def run(self, run_once: bool = False) -> None:
        """Run the bot (continuously or once).
        
        Args:
            run_once: If True, run once and exit. If False, run on schedule.
        """
        if run_once:
            self.run_analysis_cycle()
        else:
            # Schedule periodic runs
            interval = self.config.get('poll_interval_minutes', 15)
            schedule.every(interval).minutes.do(self.run_analysis_cycle)
            
            self.logger.info(f"Bot started. Running every {interval} minutes.")
            self.logger.info("Press Ctrl+C to stop.")
            
            # Run initial cycle
            self.run_analysis_cycle()
            
            # Run scheduled cycles
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Bot stopped by user")


def main():
    """Main entry point."""
    import sys
    
    run_once = '--once' in sys.argv or '-o' in sys.argv
    
    try:
        bot = PolymarketBot()
        bot.run(run_once=run_once)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
