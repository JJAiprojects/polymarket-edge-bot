#!/usr/bin/env python
"""Test script to verify bot setup and configuration."""
import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from src.config_manager import ConfigManager
        from src.logger_setup import setup_logger
        from src.database import Database
        from src.data_ingestion import PolymarketAPI
        from src.analysis import EdgeDetector
        print("[OK] All imports successful")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from src.config_manager import ConfigManager
        config = ConfigManager()
        poll_interval = config.get('poll_interval_minutes')
        print(f"[OK] Config loaded successfully (poll interval: {poll_interval} min)")
        return True
    except Exception as e:
        print(f"[ERROR] Config error: {e}")
        print("  Make sure config/config.yaml exists")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    try:
        from src.database import Database
        db = Database("data/test.db")
        print("[OK] Database initialized successfully")
        # Clean up test database (close session first)
        session = db.get_session()
        session.close()
        db.engine.dispose()
        import time
        time.sleep(0.1)  # Brief wait for file handle release
        if os.path.exists("data/test.db"):
            try:
                os.remove("data/test.db")
            except:
                pass  # Ignore if still locked
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

def test_polymarket_api():
    """Test Polymarket API connection."""
    print("\nTesting Polymarket API...")
    try:
        from src.data_ingestion import PolymarketAPI
        api = PolymarketAPI()
        markets = api.get_markets(limit=1)
        if markets:
            print(f"[OK] Polymarket API working (fetched {len(markets)} market)")
        else:
            print("[WARN] Polymarket API connected but no markets returned")
        return True
    except Exception as e:
        print(f"[ERROR] Polymarket API error: {e}")
        print("  Check your internet connection")
        return False

def test_environment():
    """Test environment variables."""
    print("\nTesting environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    import os
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    
    if telegram_token and telegram_token != 'your_telegram_bot_token_here':
        print("[OK] Telegram bot token found")
    else:
        print("[WARN] Telegram bot token not configured (optional for testing)")
    
    if telegram_chat and telegram_chat != 'your_telegram_chat_id_here':
        print("[OK] Telegram chat ID found")
    else:
        print("[WARN] Telegram chat ID not configured (optional for testing)")
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("Polymarket Bot Setup Test")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))
    results.append(("Polymarket API", test_polymarket_api()))
    results.append(("Environment", test_environment()))
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n[SUCCESS] All critical tests passed! Bot is ready to run.")
        print("\nNext steps:")
        print("1. Configure .env file with Telegram credentials (optional)")
        print("2. Run: python run.py --once")
    else:
        print("\n[ERROR] Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
