"""Configuration management for the bot."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration from YAML and environment variables."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Override with environment variables if present
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Override config values with environment variables."""
        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.config['telegram_bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
        if os.getenv('TELEGRAM_CHAT_ID'):
            self.config['telegram_chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
        
        # Discord
        if os.getenv('DISCORD_BOT_TOKEN'):
            self.config['discord_bot_token'] = os.getenv('DISCORD_BOT_TOKEN')
        if os.getenv('DISCORD_CHANNEL_ID'):
            self.config['discord_channel_id'] = os.getenv('DISCORD_CHANNEL_ID')
        
        # Twitter
        if os.getenv('TWITTER_BEARER_TOKEN'):
            self.config['twitter_bearer_token'] = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Blockchain
        if os.getenv('POLYGON_RPC_URL'):
            self.config['polygon_rpc_url'] = os.getenv('POLYGON_RPC_URL')
        if os.getenv('POLYGONSCAN_API_KEY'):
            self.config['polygonscan_api_key'] = os.getenv('POLYGONSCAN_API_KEY')
        
        # External APIs
        if os.getenv('MANIFOLD_API_KEY'):
            self.config['manifold_api_key'] = os.getenv('MANIFOLD_API_KEY')
        if os.getenv('METACULUS_API_KEY'):
            self.config['metaculus_api_key'] = os.getenv('METACULUS_API_KEY')
        
        # Environment
        self.config['environment'] = os.getenv('ENVIRONMENT', 'development')
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'telegram.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
