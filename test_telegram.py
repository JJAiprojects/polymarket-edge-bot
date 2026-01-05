#!/usr/bin/env python
"""Test Telegram notification setup."""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.notifications.telegram_notifier import TelegramNotifier

def test_telegram():
    """Test Telegram bot connection and send a test message."""
    print("=" * 60)
    print("TELEGRAM NOTIFICATION TEST")
    print("=" * 60)
    print()
    
    # Get credentials from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Check if configured
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        print("[ERROR] TELEGRAM_BOT_TOKEN not configured!")
        print("   Please add it to your .env file")
        return False
    
    if not chat_id or chat_id == 'your_telegram_chat_id_here':
        print("[ERROR] TELEGRAM_CHAT_ID not configured!")
        print("   Please add it to your .env file")
        return False
    
    print(f"[OK] Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"[OK] Chat ID: {chat_id}")
    print()
    
    # Initialize notifier
    print("Initializing Telegram notifier...")
    try:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        if not notifier.bot:
            print("[ERROR] Failed to initialize Telegram bot")
            print("   Check that your bot token is correct")
            return False
        
        print("[OK] Telegram bot initialized")
        print()
        
        # Send test message
        print("Sending test message...")
        test_message = (
            "🤖 **Polymarket Bot Test**\n\n"
            "If you receive this message, your Telegram setup is working correctly!\n\n"
            "The bot will send notifications when it detects opportunities."
        )
        
        success = notifier.send_message(test_message)
        
        if success:
            print("[SUCCESS] Test message sent!")
            print("   Check your Telegram - you should have received a message")
            return True
        else:
            print("[ERROR] Failed to send message")
            print("   Possible issues:")
            print("   - Chat ID is incorrect")
            print("   - Bot hasn't been started (send /start to your bot)")
            print("   - Bot token is invalid")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_opportunity_notification():
    """Test sending an opportunity notification."""
    print("\n" + "=" * 60)
    print("TESTING OPPORTUNITY NOTIFICATION FORMAT")
    print("=" * 60)
    print()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("[SKIP] Telegram not configured, skipping opportunity test")
        return
    
    try:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        # Create a test opportunity
        test_opportunity = {
            'market_id': 'test_market_123',
            'market_question': 'Will this test work?',
            'signal_type': 'volume_spike',
            'current_probability': 0.45,
            'expected_value': 12.50,
            'suggested_size_usd': 250.00,
            'rationale': 'This is a test opportunity to verify notification formatting works correctly.'
        }
        
        print("Sending test opportunity notification...")
        success = notifier.notify_opportunity(test_opportunity)
        
        if success:
            print("[SUCCESS] Test opportunity notification sent!")
            print("   Check your Telegram for the formatted message")
        else:
            print("[ERROR] Failed to send opportunity notification")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    print()
    success = test_telegram()
    
    if success:
        test_opportunity_notification()
    
    print("\n" + "=" * 60)
    if success:
        print("TELEGRAM SETUP: WORKING")
        print("=" * 60)
        print("\nIf you didn't receive messages, check:")
        print("1. You sent /start to your bot")
        print("2. Chat ID is correct (check .env file)")
        print("3. Bot token is correct")
    else:
        print("TELEGRAM SETUP: NEEDS ATTENTION")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Make sure .env file has TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        print("2. Bot token should start with numbers and colon (e.g., 123456789:ABC...)")
        print("3. Chat ID should be a number (e.g., 123456789)")
        print("4. Send /start to your bot first")
        print("5. For groups, use negative chat ID (e.g., -1001234567890)")
