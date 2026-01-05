# Deploy to Render.com - Step by Step Guide

## Prerequisites

1. ✅ Code is working locally
2. ✅ Telegram is configured and tested
3. ✅ GitHub account (free)
4. ✅ Render.com account (free tier available)

---

## Step 1: Prepare Your Code for GitHub

### 1.1 Create .gitignore (Already Done)
Your `.gitignore` is already set up to exclude:
- `.env` file (your secrets)
- `venv/` (virtual environment)
- `logs/` and `data/` (runtime files)

### 1.2 Initialize Git Repository

```powershell
# In your project directory
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Polymarket Edge Detection Bot"
```

---

## Step 2: Push to GitHub

### 2.1 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click **"New repository"** (or the **+** icon)
3. Repository name: `polymarket-edge-bot` (or any name you like)
4. Description: "AI bot for detecting edges on Polymarket"
5. Set to **Public** (or Private if you have GitHub Pro)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### 2.2 Push Your Code

GitHub will show you commands. Use these:

```powershell
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/polymarket-edge-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 3: Create Render Service

### 3.1 Sign Up / Log In to Render

1. Go to [Render.com](https://render.com)
2. Sign up or log in (you can use GitHub to sign in)

### 3.2 Create New Service

1. Click **"New +"** button
2. Select **"Cron Job"** (recommended for scheduled runs)
   - OR select **"Web Service"** if you want it always running

---

## Step 4: Configure Cron Job (Recommended)

### 4.1 Basic Settings

- **Name**: `polymarket-bot` (or any name)
- **Repository**: Select your GitHub repository
- **Branch**: `main`
- **Schedule**: `*/15 * * * *` (every 15 minutes)
  - Or use: `0 */1 * * *` (every hour)
  - Or use: `*/30 * * * *` (every 30 minutes)

### 4.2 Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -m src.bot --once
```

### 4.3 Environment Variables

Click **"Environment"** tab and add these variables:

```
ENVIRONMENT=production
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
TELEGRAM_CHAT_ID=your_actual_chat_id_here
POLYGON_RPC_URL=https://polygon-rpc.com
```

**Important:**
- Copy values from your `.env` file
- **DO NOT** include quotes around values
- Click **"Save Changes"** after adding each

### 4.4 Optional Environment Variables

Add these if you have them:
```
TWITTER_BEARER_TOKEN=your_twitter_token
POLYGONSCAN_API_KEY=your_polygonscan_key
MANIFOLD_API_KEY=your_manifold_key
```

### 4.5 Create Service

Click **"Create Cron Job"**

---

## Step 5: Configure Web Service (Alternative)

If you prefer a web service that runs continuously:

### 5.1 Basic Settings

- **Name**: `polymarket-bot`
- **Repository**: Select your GitHub repository
- **Branch**: `main`
- **Region**: Choose closest to you
- **Root Directory**: Leave empty (or `./`)

### 5.2 Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -m src.bot
```

### 5.3 Environment Variables

Same as Step 4.3 above.

### 5.4 Plan

- **Free Plan**: Works fine for this bot
- Click **"Create Web Service"**

---

## Step 6: Verify Deployment

### 6.1 Check Logs

1. Go to your service on Render dashboard
2. Click **"Logs"** tab
3. You should see:
   ```
   Initializing Polymarket Edge Detection Bot...
   Database initialized: data/bot_data.db
   Telegram notifications enabled
   Bot initialization complete
   Starting analysis cycle...
   ```

### 6.2 First Run

- **Cron Job**: Will run automatically on schedule
- **Web Service**: Starts immediately

### 6.3 Check Telegram

After the first run completes, check your Telegram group for notifications (if opportunities are found).

---

## Step 7: Monitor Your Bot

### 7.1 View Logs

- Render dashboard → Your service → **"Logs"** tab
- Shows real-time output from your bot

### 7.2 Check Status

- **Cron Job**: Shows last run time and next scheduled run
- **Web Service**: Shows if it's running or stopped

### 7.3 Metrics

- Free tier includes basic metrics
- Monitor CPU, memory usage

---

## Troubleshooting

### "Build Failed"

**Issue**: Dependencies not installing
**Fix**: 
- Check `requirements.txt` is in root directory
- Check Python version (Render uses Python 3.11 by default)

### "Service Crashed"

**Issue**: Bot error on startup
**Fix**:
- Check logs for error messages
- Verify all environment variables are set
- Check database path (should work on Render's disk)

### "No Messages Received"

**Issue**: Bot runs but no Telegram messages
**Fix**:
- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
- Check logs for "Telegram notifications enabled"
- Remember: Bot only sends messages when opportunities are detected

### "Python Not Found"

**Issue**: Wrong Python version
**Fix**:
- Render uses Python 3.11 by default
- If needed, add to build command: `python3.11 -m pip install -r requirements.txt`

---

## Recommended Settings

### For Cron Job:
- **Schedule**: `*/15 * * * *` (every 15 minutes)
- **Build**: `pip install -r requirements.txt`
- **Start**: `python -m src.bot --once`

### For Web Service:
- **Build**: `pip install -r requirements.txt`
- **Start**: `python -m src.bot`
- **Auto-Deploy**: Enable (updates automatically on git push)

---

## Cost

**Free Tier Includes:**
- ✅ 750 hours/month of runtime
- ✅ 100 GB bandwidth
- ✅ Persistent disk (for database)
- ✅ Cron jobs included

**For this bot:**
- Cron job running every 15 min = ~720 runs/month = **Well within free tier!**

---

## Next Steps After Deployment

1. ✅ Monitor first few runs in logs
2. ✅ Verify Telegram notifications work
3. ✅ Adjust thresholds in `config/config.yaml` if needed
4. ✅ Push updates: Just `git push` and Render auto-deploys (if enabled)

---

## Quick Reference

### Update Your Bot

```powershell
# Make changes locally
# Then:
git add .
git commit -m "Update bot configuration"
git push
```

Render will automatically rebuild and redeploy!

### View Logs

Render Dashboard → Your Service → Logs tab

### Stop/Start Service

Render Dashboard → Your Service → Manual Deploy → Stop/Start

---

## Summary

1. ✅ Push code to GitHub
2. ✅ Create Render account
3. ✅ Create Cron Job (or Web Service)
4. ✅ Add environment variables
5. ✅ Deploy and monitor

Your bot will now run automatically on Render! 🚀
