"""Telegram notification handler."""
from telegram import Bot
from telegram.error import TelegramError
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        try:
            self.bot = Bot(token=bot_token)
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
    
    def send_message(self, message: str) -> bool:
        """Send a text message (synchronous wrapper for async method).
        
        Args:
            message: Message text
            
        Returns:
            True if sent successfully
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized")
            return False
        
        try:
            # Run async method synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self._send_message_async(message)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def _send_message_async(self, message: str) -> bool:
        """Async method to send message.
        
        Args:
            message: Message text
            
        Returns:
            True if sent successfully
        """
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def format_opportunity_message(self, opportunity: Dict[str, Any]) -> str:
        """Format an opportunity as a Telegram message.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Formatted message string
        """
        market_id = opportunity.get('market_id', 'N/A')
        market_question = opportunity.get('market_question', 'Unknown Market')
        signal_type = opportunity.get('signal_type', 'unknown')
        current_prob = opportunity.get('current_probability', 0.0)
        ev = opportunity.get('expected_value', 0.0)
        suggested_size = opportunity.get('suggested_size_usd', 0.0)
        rationale = opportunity.get('rationale', 'No rationale provided')
        
        message = f"🚨 <b>Flagged Opportunity</b>\n\n"
        message += f"<b>Market:</b> {market_question}\n"
        message += f"<b>Signal:</b> {signal_type.replace('_', ' ').title()}\n"
        message += f"<b>Current Probability:</b> {current_prob:.1%}\n"
        message += f"<b>Expected Value:</b> ${ev:.2f}\n"
        message += f"<b>Suggested Size:</b> ${suggested_size:.2f}\n\n"
        message += f"<b>Rationale:</b>\n{rationale}\n\n"
        message += f"<a href='https://polymarket.com/event/{market_id}'>View on Polymarket</a>"
        
        return message
    
    def notify_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Notify about a flagged opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            True if sent successfully
        """
        message = self.format_opportunity_message(opportunity)
        return self.send_message(message)
    
    def send_alert(self, title: str, message: str) -> bool:
        """Send a general alert.
        
        Args:
            title: Alert title
            message: Alert message
            
        Returns:
            True if sent successfully
        """
        formatted = f"⚠️ <b>{title}</b>\n\n{message}"
        return self.send_message(formatted)
