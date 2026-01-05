# Quick Start - Step by Step

## ✅ Step 1: Verify Python is Installed

Open PowerShell and run:
```powershell
C:\Users\jjwho\AppData\Local\Programs\Python\Python312\python.exe --version
```

You should see: `Python 3.12.10`

If you see an error, Python needs to be installed. See `INSTALL_PYTHON.md`.

---

## ✅ Step 2: Navigate to Your Project

Open PowerShell and type:
```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
```

---

## ✅ Step 3: Set Up Virtual Environment (First Time Only)

Run this command:
```powershell
C:\Users\jjwho\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
```

Wait for it to complete (about 10 seconds).

---

## ✅ Step 4: Activate Virtual Environment

Run this command:
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error**, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Type `Y` when prompted, then try Step 4 again.

You should see `(venv)` at the start of your prompt.

---

## ✅ Step 5: Install Dependencies (First Time Only)

With venv activated, run:
```powershell
pip install -r requirements.txt
```

This will take 1-2 minutes. Wait for it to finish.

---

## ✅ Step 6: Test the Setup

Run:
```powershell
python test_setup.py
```

You should see all tests pass with `[PASS]` or `[OK]`.

---

## ✅ Step 7: Run the Bot

### Option A: Run Once (Test Mode)
```powershell
python run.py --once
```

### Option B: Run Continuously
```powershell
python run.py
```

### Option C: Use Helper Script
```powershell
.\run_bot.ps1 --once
```
or
```powershell
.\run_bot.bat --once
```

---

## 🚀 Quick Commands Reference

```powershell
# Navigate to project
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run bot once
python run.py --once

# Run bot continuously
python run.py

# Deactivate virtual environment (when done)
deactivate
```

---

## ⚠️ If Python Command Doesn't Work

If `python` command doesn't work, use the full path:

```powershell
# Instead of: python run.py --once
# Use this:
C:\Users\jjwho\AppData\Local\Programs\Python\Python312\python.exe run.py --once
```

Or use the helper scripts:
```powershell
.\run_bot.ps1 --once
```

---

## 📝 What to Expect

When you run `python run.py --once`, you should see:
- Bot initializing
- Fetching markets from Polymarket
- Analyzing markets
- Log messages in the console
- Log file created in `logs/` directory

If opportunities are found, you'll see them logged (and get Telegram notifications if configured).

---

## 🆘 Still Having Issues?

1. Make sure you're in the correct directory
2. Make sure virtual environment is activated (you see `(venv)` in prompt)
3. Try using the full Python path (see above)
4. Check `INSTALL_PYTHON.md` for Python installation help
5. Check `logs/` directory for error messages
