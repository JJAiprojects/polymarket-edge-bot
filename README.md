# Polymarket Edge Detection Bot

An AI-powered bot that analyzes Polymarket prediction markets to detect edges, insider movements, and early opportunities before the crowd. The bot monitors volume spikes, probability divergences, smart wallet activity, Twitter signals, and more.

## Features

- **Volume Spike Detection**: Identifies unusual trading volume patterns
- **Smart Wallet Tracking**: Monitors wallets with proven track records
- **Probability Divergence**: Compares Polymarket probabilities with external sources (Manifold, Metaculus)
- **Twitter Signal Detection**: Monitors social media for early market signals
- **Correlation Analysis**: Detects divergences in correlated markets
- **Position Sizing**: Uses Kelly Criterion for optimal bet sizing
- **Risk Management**: Enforces position limits, exposure caps, and diversification
- **Notifications**: Sends alerts via Telegram or Discord

## Project Structure

```
Polymarket_EdgeDetectionBot/
├── config/
│   └── config.yaml          # Configuration file
├── src/
│   ├── __init__.py
│   ├── bot.py                # Main bot orchestrator
│   ├── config_manager.py     # Configuration management
│   ├── logger_setup.py       # Logging configuration
│   ├── database.py           # Database layer (SQLite)
│   ├── data_ingestion/
│   │   ├── __init__.py
│   │   ├── polymarket_api.py # Polymarket Gamma API client
│   │   ├── blockchain.py     # Polygon blockchain monitor
│   │   ├── external_apis.py  # External API integrations
│   │   └── twitter_monitor.py # Twitter monitoring
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── edge_detector.py  # Edge detection logic
│   │   ├── position_sizing.py # Kelly Criterion sizing
│   │   ├── risk_manager.py   # Risk management
│   │   └── correlation_analyzer.py # Correlation analysis
│   └── notifications/
│       ├── __init__.py
│       ├── telegram_notifier.py # Telegram notifications
│       └── discord_notifier.py  # Discord notifications
├── data/                      # Database files (gitignored)
├── logs/                      # Log files (gitignored)
├── requirements.txt           # Python dependencies
├── env.example                # Environment variables template
├── .gitignore
└── README.md
```

## Setup

### 1. Clone and Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Copy the environment variables template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and fill in your API keys:
   - `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/botfather)
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID
   - `TWITTER_BEARER_TOKEN`: Twitter API v2 bearer token (optional)
   - `POLYGON_RPC_URL`: Polygon RPC endpoint (default public endpoint works)
   - `POLYGONSCAN_API_KEY`: Optional, for wallet age analysis

3. Edit `config/config.yaml` to adjust:
   - Polling intervals
   - Detection thresholds
   - Risk parameters
   - Market categories to monitor

### 3. Run Locally

```bash
# Run once (for testing)
python -m src.bot --once

# Run continuously (scheduled)
python -m src.bot
```

## Configuration

### Key Parameters in `config/config.yaml`

- `poll_interval_minutes`: How often to run analysis (default: 15)
- `volume_spike_multiplier`: Volume spike threshold (default: 4.0x)
- `divergence_threshold_pct`: Probability divergence threshold (default: 12%)
- `kelly_fraction`: Fractional Kelly multiplier (default: 0.5)
- `max_exposure_pct`: Maximum portfolio exposure (default: 40%)
- `notification_threshold_ev`: Minimum EV to flag (default: $0.05)

See `config/config.yaml` for all available parameters.

## Deployment to Render.com

### 1. Prepare for Deployment

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

### 2. Create Render Service

1. Go to [Render.com](https://render.com) and create a new "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.bot`
   - **Environment**: Python 3

### 3. Set Environment Variables

In Render dashboard, add environment variables from your `.env` file:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TWITTER_BEARER_TOKEN` (optional)
- `POLYGON_RPC_URL`
- `POLYGONSCAN_API_KEY` (optional)
- `ENVIRONMENT=production`

### 4. Alternative: Cron Job

For scheduled runs instead of always-on service:

1. Create a "Cron Job" on Render
2. Set schedule: `*/15 * * * *` (every 15 minutes)
3. Build: `pip install -r requirements.txt`
4. Command: `python -m src.bot --once`

## Usage

### Running the Bot

The bot will:
1. Fetch active markets from Polymarket
2. Analyze each market for edges and signals
3. Calculate position sizes using Kelly Criterion
4. Check risk constraints
5. Flag opportunities and send notifications

### Monitoring

- Check logs in `logs/` directory
- Review flagged opportunities in database: `data/bot_data.db`
- Receive notifications via Telegram/Discord

### Database

The bot uses SQLite to store:
- Market data and historical probabilities
- Trade history
- Wallet tracking
- Flagged opportunities (journal)

You can query the database using SQLite tools or Python.

## Development

### Testing Locally

```bash
# Run with debug logging
# Edit config.yaml: log_level: "DEBUG"
python -m src.bot --once
```

### Adding New Signals

1. Add detection logic in `src/analysis/edge_detector.py`
2. Call from `src/bot.py` in `analyze_market()`
3. Update notification formatting if needed

### Extending External APIs

1. Add API client in `src/data_ingestion/external_apis.py`
2. Integrate in `src/bot.py`
3. Update configuration as needed

## Security Notes

- Never commit `.env` file (already in `.gitignore`)
- Use environment variables in production (Render)
- Keep API keys secure
- Review and adjust risk parameters before live trading

## Limitations

- **Read-only**: Bot flags opportunities but doesn't execute trades
- **API Rate Limits**: Respects Polymarket and external API limits
- **Data Availability**: Some features require API keys (Twitter, PolygonScan)
- **Correlation Analysis**: Requires historical data to build up

## Future Enhancements

- [ ] Auto-trading via Polymarket CLOB API
- [ ] Advanced NLP for Twitter sentiment
- [ ] Machine learning for probability estimation
- [ ] Web dashboard for monitoring
- [ ] Backtesting framework
- [ ] Integration with Kalshi/PredictIt for arbitrage

## License

MIT License - See LICENSE file for details

## Disclaimer

This bot is for educational and research purposes. Trading prediction markets involves risk. Always do your own research and never invest more than you can afford to lose.
