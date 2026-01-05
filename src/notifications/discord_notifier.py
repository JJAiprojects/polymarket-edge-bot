"""Discord notification handler."""
import discord
from discord import Embed
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Send notifications via Discord."""
    
    def __init__(self, bot_token: str, channel_id: int):
        """Initialize Discord notifier.
        
        Args:
            bot_token: Discord bot token
            channel_id: Channel ID to send messages to
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.client = None
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = discord.Client(intents=intents)
        except Exception as e:
            logger.error(f"Failed to initialize Discord client: {e}")
    
    async def send_message(self, content: str, embed: Optional[Embed] = None) -> bool:
        """Send a message to Discord channel.
        
        Args:
            content: Message content
            embed: Optional embed object
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.warning("Discord client not initialized")
            return False
        
        try:
            channel = await self.client.fetch_channel(self.channel_id)
            await channel.send(content=content, embed=embed)
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord message: {e}")
            return False
    
    def create_opportunity_embed(self, opportunity: Dict[str, Any]) -> Embed:
        """Create a Discord embed for an opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Discord Embed object
        """
        market_id = opportunity.get('market_id', 'N/A')
        market_question = opportunity.get('market_question', 'Unknown Market')
        signal_type = opportunity.get('signal_type', 'unknown')
        current_prob = opportunity.get('current_probability', 0.0)
        ev = opportunity.get('expected_value', 0.0)
        suggested_size = opportunity.get('suggested_size_usd', 0.0)
        rationale = opportunity.get('rationale', 'No rationale provided')
        
        embed = Embed(
            title="🚨 Flagged Opportunity",
            description=market_question,
            color=0x00ff00 if ev > 0 else 0xff0000
        )
        
        embed.add_field(name="Signal Type", value=signal_type.replace('_', ' ').title(), inline=True)
        embed.add_field(name="Current Probability", value=f"{current_prob:.1%}", inline=True)
        embed.add_field(name="Expected Value", value=f"${ev:.2f}", inline=True)
        embed.add_field(name="Suggested Size", value=f"${suggested_size:.2f}", inline=True)
        embed.add_field(name="Rationale", value=rationale[:1024], inline=False)
        embed.add_field(
            name="Link",
            value=f"[View on Polymarket](https://polymarket.com/event/{market_id})",
            inline=False
        )
        
        return embed
    
    async def notify_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Notify about a flagged opportunity.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            True if sent successfully
        """
        embed = self.create_opportunity_embed(opportunity)
        return await self.send_message("", embed=embed)
    
    async def send_alert(self, title: str, message: str) -> bool:
        """Send a general alert.
        
        Args:
            title: Alert title
            message: Alert message
            
        Returns:
            True if sent successfully
        """
        embed = Embed(title=title, description=message, color=0xffaa00)
        return await self.send_message("", embed=embed)
