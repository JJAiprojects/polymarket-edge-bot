# How to Use External Terminal (If Cursor Terminal Doesn't Work)

If you can't type in Cursor's terminal, use Windows PowerShell or Command Prompt instead!

---

## Method 1: Use Windows PowerShell (Recommended)

### Step 1: Open PowerShell
1. Press `Windows Key`
2. Type "PowerShell"
3. Click "Windows PowerShell"

### Step 2: Navigate to Your Project
Copy and paste this command:
```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
```

### Step 3: Activate Virtual Environment
Copy and paste this:
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Type `Y` and press Enter, then try again.

### Step 4: Run the Bot
```powershell
python run.py --once
```

---

## Method 2: Use Command Prompt

### Step 1: Open Command Prompt
1. Press `Windows Key`
2. Type "cmd"
3. Click "Command Prompt"

### Step 2: Navigate to Your Project
Copy and paste:
```cmd
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate.bat
```

### Step 4: Run the Bot
```cmd
python run.py --once
```

---

## Method 3: Double-Click Scripts (Easiest!)

I created batch files you can just double-click:

### Run Once:
1. Open File Explorer
2. Navigate to: `C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot`
3. **Double-click** `RUN_BOT.bat`
4. A window will open and run the bot!

### Run Continuously:
1. **Double-click** `RUN_BOT_CONTINUOUS.bat`
2. Bot will run every 15 minutes
3. Press `Ctrl+C` in the window to stop

---

## Method 4: Create Desktop Shortcut

### Step 1: Right-click `RUN_BOT.bat`
### Step 2: Select "Create shortcut"
### Step 3: Drag shortcut to Desktop
### Step 4: Double-click from Desktop anytime!

---

## Quick Commands Reference

Once you're in PowerShell/CMD in your project directory:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run bot once
python run.py --once

# Run bot continuously
python run.py

# Test bot detection
python test_bot.py

# Test setup
python test_setup.py
```

---

## Troubleshooting

### "Python not found"
Use the full path:
```powershell
C:\Users\jjwho\AppData\Local\Programs\Python\Python312\python.exe run.py --once
```

### "Cannot activate venv"
Make sure you're in the project directory:
```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
```

### Batch file doesn't work
- Right-click the `.bat` file
- Select "Run as administrator"
- Or use PowerShell/CMD method instead

---

## Recommended: Use Method 3 (Double-Click)

**Just double-click `RUN_BOT.bat`** - it's the easiest way!

The batch file will:
- ✅ Find Python automatically
- ✅ Activate virtual environment
- ✅ Run the bot
- ✅ Show you the output
- ✅ Wait for you to press a key when done

No typing needed! 🎉
