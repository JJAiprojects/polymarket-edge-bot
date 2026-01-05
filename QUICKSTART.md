# Quick Start Guide

## 1. Initial Setup (5 minutes)

### Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Configure Environment
```bash
# Copy environment template
copy env.example .env  # Windows
# or
cp env.example .env    # Mac/Linux

# Edit .env and add at minimum:
# - TELEGRAM_BOT_TOKEN (get from @BotFather on Telegram)
# - TELEGRAM_CHAT_ID (your Telegram user ID)
```

### Get Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token to `.env` as `TELEGRAM_BOT_TOKEN`
4. Send `/start` to your bot, then visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Find your `chat.id` in the response and add to `.env` as `TELEGRAM_CHAT_ID`

## 2. First Test Run

```bash
# Run once to test (no scheduling)
python run.py --once

# Or directly:
python -m src.bot --once
```

Expected output:
- Bot initializes successfully
- Fetches markets from Polymarket
- Analyzes markets (may take a minute)
- Logs results to console and `logs/` directory

## 3. Run Continuously

```bash
# Run with scheduled polling (every 15 minutes by default)
python run.py

# Press Ctrl+C to stop
```

## 4. Verify It's Working

1. **Check Logs**: Look in `logs/` directory for daily log files
2. **Check Database**: Database file created at `data/bot_data.db`
3. **Check Notifications**: If opportunities are found, you'll receive Telegram messages

## 5. Customize Configuration

Edit `config/config.yaml` to adjust:
- `poll_interval_minutes`: How often to check (default: 15)
- `volume_spike_multiplier`: Sensitivity for volume spikes (default: 4.0)
- `notification_threshold_ev`: Minimum expected value to notify (default: 0.05)
- `monitor_categories`: Which market categories to watch

## Troubleshooting

### "Config file not found"
- Make sure `config/config.yaml` exists
- Check you're running from project root directory

### "No module named 'src'"
- Make sure you're in the project root
- Try: `python -m src.bot` instead of `python src/bot.py`

### "Telegram bot not initialized"
- Check `.env` file exists and has `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Verify token is correct (no extra spaces)

### "API request failed"
- Check internet connection
- Polymarket API may be temporarily down
- Check rate limits in config (default: 60 requests/min)

### No opportunities detected
- This is normal! The bot only flags real edges
- Lower `notification_threshold_ev` in config to see more signals
- Check logs for detailed analysis

## Next Steps

1. **Monitor for a few hours** to see what gets flagged
2. **Adjust thresholds** in `config/config.yaml` based on your preferences
3. **Review flagged opportunities** in the database or logs
4. **Deploy to Render.com** when ready (see README.md)

## Testing Individual Components

```python
# Test Polymarket API
from src.data_ingestion import PolymarketAPI
api = PolymarketAPI()
markets = api.get_markets(category='politics', limit=5)
print(f"Found {len(markets)} markets")

# Test configuration
from src.config_manager import ConfigManager
config = ConfigManager()
print(f"Poll interval: {config.get('poll_interval_minutes')} minutes")

# Test database
from src.database import Database
db = Database()
print("Database initialized")
```

## Production Deployment

See `README.md` for detailed deployment instructions to Render.com.
