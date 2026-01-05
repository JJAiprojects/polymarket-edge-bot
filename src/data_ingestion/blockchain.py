"""Blockchain monitoring for Polygon network."""
from web3 import Web3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import requests

logger = logging.getLogger(__name__)


class BlockchainMonitor:
    """Monitor Polygon blockchain for Polymarket activity."""
    
    def __init__(self, rpc_url: str, polygonscan_api_key: Optional[str] = None):
        """Initialize blockchain monitor.
        
        Args:
            rpc_url: Polygon RPC endpoint URL
            polygonscan_api_key: Optional PolygonScan API key for enhanced queries
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.polygonscan_api_key = polygonscan_api_key
        self.polygonscan_base = "https://api.polygonscan.com/api"
        
        if not self.w3.is_connected():
            logger.warning("Failed to connect to Polygon RPC")
    
    def get_wallet_age(self, address: str) -> Optional[int]:
        """Get wallet age in hours.
        
        Args:
            address: Wallet address
            
        Returns:
            Age in hours, or None if unable to determine
        """
        if not self.polygonscan_api_key:
            logger.debug("PolygonScan API key not provided, skipping wallet age check")
            return None
        
        try:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'sort': 'asc',
                'apikey': self.polygonscan_api_key
            }
            
            response = requests.get(self.polygonscan_base, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == '1' and data.get('result'):
                first_tx = data['result'][0]
                first_tx_time = int(first_tx.get('timeStamp', 0))
                if first_tx_time:
                    age_seconds = int(datetime.now().timestamp()) - first_tx_time
                    return age_seconds // 3600  # Convert to hours
            
            return None
        except Exception as e:
            logger.error(f"Error getting wallet age for {address}: {e}")
            return None
    
    def is_fresh_wallet(self, address: str, threshold_hours: int = 24) -> bool:
        """Check if wallet is 'fresh' (newly created).
        
        Args:
            address: Wallet address
            threshold_hours: Age threshold in hours
            
        Returns:
            True if wallet is fresh
        """
        age = self.get_wallet_age(address)
        if age is None:
            return False
        return age < threshold_hours
    
    def get_wallet_transaction_count(self, address: str) -> int:
        """Get total transaction count for a wallet.
        
        Args:
            address: Wallet address
            
        Returns:
            Transaction count
        """
        try:
            return self.w3.eth.get_transaction_count(address)
        except Exception as e:
            logger.error(f"Error getting transaction count for {address}: {e}")
            return 0
    
    def get_contract_events(
        self,
        contract_address: str,
        event_signature: str,
        from_block: int = 0,
        to_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get contract events (for future use with Polymarket contracts).
        
        Args:
            contract_address: Contract address
            event_signature: Event signature hash
            from_block: Starting block
            to_block: Ending block (None for latest)
            
        Returns:
            List of event logs
        """
        try:
            if to_block is None:
                to_block = self.w3.eth.block_number
            
            event_filter = self.w3.eth.filter({
                'fromBlock': from_block,
                'toBlock': to_block,
                'address': contract_address,
                'topics': [event_signature]
            })
            
            return event_filter.get_all_entries()
        except Exception as e:
            logger.error(f"Error getting contract events: {e}")
            return []
