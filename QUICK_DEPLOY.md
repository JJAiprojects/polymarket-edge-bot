# Quick Deploy to Render - 5 Minutes

## Fast Track Steps

### 1. Push to GitHub (2 min)

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/polymarket-edge-bot.git
git push -u origin main
```

### 2. Create Render Cron Job (2 min)

1. Go to [render.com](https://render.com) → New → Cron Job
2. Connect GitHub repo
3. Settings:
   - **Schedule**: `*/15 * * * *`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `python -m src.bot --once`
4. Add Environment Variables:
   - `TELEGRAM_BOT_TOKEN` = (from your .env)
   - `TELEGRAM_CHAT_ID` = (from your .env)
   - `ENVIRONMENT` = `production`
5. Click **Create Cron Job**

### 3. Done! (1 min)

- Bot runs every 15 minutes automatically
- Check logs in Render dashboard
- Check Telegram for notifications

---

## That's It! 🎉

Your bot is now live on Render and will run automatically!
