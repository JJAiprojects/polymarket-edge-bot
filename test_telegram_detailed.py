#!/usr/bin/env python
"""Detailed Telegram test with error reporting."""
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

import asyncio
from telegram import Bot
from telegram.error import TelegramError, BadRequest
try:
    from telegram.error import Unauthorized
except ImportError:
    # For newer versions
    from telegram.error import Forbidden as Unauthorized

async def test_telegram_async():
    """Test Telegram with detailed error reporting."""
    print("=" * 60)
    print("DETAILED TELEGRAM TEST")
    print("=" * 60)
    print()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or bot_token == 'your_telegram_bot_token_here':
        print("[ERROR] TELEGRAM_BOT_TOKEN not configured!")
        return False
    
    if not chat_id or chat_id == 'your_telegram_chat_id_here':
        print("[ERROR] TELEGRAM_CHAT_ID not configured!")
        return False
    
    print(f"Bot Token: {bot_token[:15]}...{bot_token[-5:]}")
    print(f"Chat ID: {chat_id}")
    print()
    
    try:
        # Initialize bot
        bot = Bot(token=bot_token)
        print("[OK] Bot initialized")
        
        # Test 1: Get bot info
        print("\n[TEST 1] Getting bot information...")
        try:
            bot_info = await bot.get_me()
            print(f"[OK] Bot username: @{bot_info.username}")
            print(f"[OK] Bot name: {bot_info.first_name}")
        except Unauthorized:
            print("[ERROR] Bot token is invalid!")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to get bot info: {e}")
            return False
        
        # Test 2: Send simple message
        print("\n[TEST 2] Sending simple test message...")
        try:
            message = "Test message from Polymarket Bot"
            result = await bot.send_message(chat_id=chat_id, text=message)
            print(f"[SUCCESS] Message sent! Message ID: {result.message_id}")
            print("   Check your Telegram - you should see this message")
            return True
        except BadRequest as e:
            print(f"[ERROR] Bad Request: {e}")
            if "chat not found" in str(e).lower():
                print("   -> Chat ID is incorrect or bot hasn't been added to chat")
            elif "not enough rights" in str(e).lower():
                print("   -> Bot doesn't have permission to send messages")
            return False
        except Unauthorized:
            print("[ERROR] Bot is unauthorized")
            print("   -> Bot token might be wrong or bot was deleted")
            return False
        except TelegramError as e:
            print(f"[ERROR] Telegram error: {e}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run async test."""
    try:
        result = asyncio.run(test_telegram_async())
        print("\n" + "=" * 60)
        if result:
            print("RESULT: SUCCESS - Check your Telegram!")
        else:
            print("RESULT: FAILED - See errors above")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
