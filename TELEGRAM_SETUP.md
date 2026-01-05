# Telegram Setup Guide

## Step 1: Get Your Telegram Bot Token

1. **Open Telegram** on your phone or computer
2. **Search for** `@BotFather` (official Telegram bot creator)
3. **Send this command**: `/newbot`
4. **Follow the prompts**:
   - Choose a name for your bot (e.g., "Polymarket Edge Bot")
   - Choose a username (must end in "bot", e.g., "polymarket_edge_bot")
5. **Copy the token** - BotFather will give you a token like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   **SAVE THIS TOKEN!**

---

## Step 2: Get Your Chat ID

### Method 1: Using @userinfobot (Easiest)

1. **Search for** `@userinfobot` on Telegram
2. **Start a chat** with it
3. It will reply with your user ID (a number like `123456789`)
4. **Copy this number**

### Method 2: Using Your Bot

1. **Start a chat** with your new bot (search for the username you created)
2. **Send** `/start` to your bot
3. **Open this URL in your browser** (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. **Look for** `"chat":{"id":123456789}` in the response
5. **Copy the number** after `"id":`

### Method 3: For Group Chats

If you want notifications in a **group**:
1. Add your bot to the group
2. Make the bot an admin (optional but recommended)
3. Send a message in the group
4. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
5. Find the group chat ID (it will be negative, like `-1001234567890`)

---

## Step 3: Configure Your Bot

1. **Open the `.env` file** in your project directory:
   ```
   C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot\.env
   ```

2. **Edit these lines**:
   ```env
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

3. **Save the file**

---

## Step 4: Test Your Setup

Run the bot once to test:
```powershell
python run.py --once
```

If configured correctly, you should see:
```
Telegram notifications enabled
```

When an opportunity is found, you'll receive a message like:
```
🚨 Flagged Opportunity

Market: Will Trump win the 2024 election?
Signal: Volume Spike
Current Probability: 45.0%
Expected Value: $8.50
Suggested Size: $150.00

Rationale:
Volume spike detected: 4.2x average volume.
Edge: 5.20%. Expected Value: $8.50. Suggested position: $150.00 (1.5% of bankroll).

View on Polymarket
```

---

## Troubleshooting

### "Telegram bot not initialized"
- Check that `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Make sure there are no extra spaces
- Restart the bot after changing `.env`

### "Telegram chat ID not configured"
- Check that `TELEGRAM_CHAT_ID` is correct in `.env`
- Make sure it's a number (no quotes)
- For groups, use the negative number

### Bot doesn't respond
- Make sure you sent `/start` to your bot first
- Check that the bot token is correct
- Verify the chat ID is correct

---

## Example .env File

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Other settings...
ENVIRONMENT=development
```

---

## Security Note

⚠️ **Never share your bot token or commit `.env` to GitHub!**
- The `.env` file is already in `.gitignore`
- Keep your token secret
- If token is leaked, revoke it in BotFather and create a new one
