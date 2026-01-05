# Answers to Your Questions

## 1. What does "Portfolio: 0 positions, $0.00 exposure (0.0%)" mean?

This is a **status report** showing your current portfolio state:

- **0 positions** = You have no open/active flagged opportunities right now
- **$0.00 exposure** = You have $0 currently invested/allocated
- **0.0%** = 0% of your $10,000 bankroll is currently exposed

**This is NORMAL and EXPECTED** when:
- The bot just started
- No opportunities have been flagged yet
- All previous opportunities have been resolved/closed

**It will change when:**
- The bot flags an opportunity → positions increase
- You take a position → exposure increases
- The bot tracks your portfolio over time

Think of it like a bank account balance - it starts at $0 and changes as you make transactions.

---

## 2. How to Test the Bot Works (Before Something Happens)

### Option A: Run the Test Script (Recommended)

I created a test script that uses **lowered thresholds** to verify detection works:

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Run the test
python test_bot.py
```

This will:
- ✅ Test with lower thresholds (more sensitive)
- ✅ Show you what it's detecting
- ✅ Verify all detection systems work
- ✅ Give you confidence the bot is functioning

### Option B: Lower Thresholds Temporarily

Edit `config/config.yaml` and temporarily lower these values:

```yaml
# Make it more sensitive for testing
notification_threshold_ev: 0.01  # Lower from 0.05
volume_spike_multiplier: 2.0     # Lower from 4.0
divergence_threshold_pct: 5.0    # Lower from 12.0
min_trade_size_usd: 100          # Lower from 1000
```

Then run:
```powershell
python run.py --once
```

**Remember to change them back** after testing!

### Option C: Check Historical Data

The bot stores data in the database. You can verify it's working by:

1. **Check the database exists:**
   ```powershell
   # Database should be at:
   data/bot_data.db
   ```

2. **Check logs:**
   ```powershell
   # Logs are in:
   logs/bot_YYYYMMDD.log
   ```

3. **Verify it's fetching markets:**
   - Look for "Analyzing X markets" in the output
   - This confirms it's connecting to Polymarket API

### Option D: Monitor Continuously

Run the bot continuously and watch for activity:

```powershell
python run.py
```

It will run every 15 minutes. When real market events happen (news, volatility), you'll see detections.

---

## 3. Where to Enter Telegram Bot and Group Keys

### Step 1: Find Your `.env` File

The `.env` file is in your project root:
```
C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot\.env
```

**If it doesn't exist**, copy from the template:
```powershell
Copy-Item env.example .env
```

### Step 2: Get Your Telegram Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts to create a bot
5. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Get Your Chat ID

**For Personal Chat:**
1. Start a chat with your bot
2. Send `/start`
3. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. Find `"chat":{"id":123456789}` in the response
5. Copy the number

**For Group Chat:**
1. Add your bot to the group
2. Send a message in the group
3. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. Find the group chat ID (will be negative, like `-1001234567890`)

### Step 4: Edit `.env` File

Open `.env` in any text editor and edit these lines:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Important:**
- Replace with your actual token and chat ID
- No quotes needed
- No spaces around the `=`
- Save the file

### Step 5: Test It

Run the bot:
```powershell
python run.py --once
```

You should see:
```
Telegram notifications enabled
```

When an opportunity is found, you'll get a Telegram message!

---

## Quick Reference

### Check Portfolio Status
```powershell
# The portfolio message shows:
# - How many positions you have
# - Total $ exposure
# - % of bankroll used
```

### Test Bot Detection
```powershell
python test_bot.py
```

### Configure Telegram
1. Edit `.env` file
2. Add `TELEGRAM_BOT_TOKEN=your_token`
3. Add `TELEGRAM_CHAT_ID=your_chat_id`
4. Save and restart bot

### Verify Bot is Working
- ✅ Sees "Analyzing X markets" message
- ✅ Database file exists (`data/bot_data.db`)
- ✅ Log files created (`logs/` directory)
- ✅ No error messages
- ✅ "Analysis cycle complete" message

---

## Still Not Sure?

Run this diagnostic:
```powershell
python test_setup.py
```

This will verify:
- ✅ All imports work
- ✅ Configuration loads
- ✅ Database works
- ✅ Polymarket API connects
- ✅ Telegram configured (if you set it up)

---

## Summary

1. **Portfolio message** = Status report (0 positions is normal at start)
2. **Test bot** = Run `python test_bot.py` with lowered thresholds
3. **Telegram setup** = Edit `.env` file with bot token and chat ID

See `TELEGRAM_SETUP.md` for detailed Telegram setup instructions!
