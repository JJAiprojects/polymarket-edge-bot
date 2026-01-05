# Step-by-Step Python Installation Guide

## Method 1: Install Python via Microsoft Store (Easiest)

### Step 1: Open Microsoft Store
1. Press `Windows Key` on your keyboard
2. Type "Microsoft Store" and open it

### Step 2: Search for Python
1. In the Microsoft Store, search for "Python 3.12"
2. Click on "Python 3.12" by Python Software Foundation
3. Click "Install" or "Get"

### Step 3: Wait for Installation
- Wait for Python to download and install (about 2-3 minutes)

### Step 4: Verify Installation
1. Close your current PowerShell/terminal window
2. Open a NEW PowerShell window
3. Navigate to your project:
   ```powershell
   cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
   ```
4. Test Python:
   ```powershell
   python --version
   ```
   You should see: `Python 3.12.x`

---

## Method 2: Install Python via Official Website (More Control)

### Step 1: Download Python
1. Open your web browser
2. Go to: https://www.python.org/downloads/
3. Click the big yellow "Download Python 3.12.x" button
4. The installer will download (about 25 MB)

### Step 2: Run the Installer
1. Find the downloaded file (usually in `Downloads` folder)
2. Double-click `python-3.12.x-amd64.exe`
3. **IMPORTANT**: Check the box that says **"Add Python to PATH"** at the bottom
4. Click "Install Now"
5. Wait for installation (2-3 minutes)

### Step 3: Verify Installation
1. Close ALL PowerShell/terminal windows
2. Open a NEW PowerShell window
3. Navigate to your project:
   ```powershell
   cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
   ```
4. Test Python:
   ```powershell
   python --version
   ```
   You should see: `Python 3.12.x`

---

## Method 3: Use Winget (If you have it)

### Step 1: Open PowerShell as Administrator
1. Right-click on Start button
2. Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

### Step 2: Install Python
Copy and paste this command:
```powershell
winget install Python.Python.3.12
```

### Step 3: Refresh PATH
After installation, close and reopen PowerShell, then:
```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
python --version
```

---

## After Installation: Set Up Your Project

### Step 1: Navigate to Project
```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Test the Bot
```powershell
python run.py --once
```

---

## Troubleshooting

### "Python was not found" Error

**Solution 1: Use Full Path**
```powershell
# Find where Python is installed
where.exe python

# Or use the full path directly
C:\Users\jjwho\AppData\Local\Programs\Python\Python312\python.exe --version
```

**Solution 2: Add Python to PATH Manually**
1. Press `Windows Key` and type "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", find "Path" and click "Edit"
5. Click "New" and add:
   ```
   C:\Users\jjwho\AppData\Local\Programs\Python\Python312
   C:\Users\jjwho\AppData\Local\Programs\Python\Python312\Scripts
   ```
6. Click OK on all windows
7. Close and reopen PowerShell

**Solution 3: Use Python from Virtual Environment**
If Python is installed but not in PATH, you can use the venv Python directly:
```powershell
.\venv\Scripts\python.exe run.py --once
```

### "Execution Policy" Error

If you see: `cannot be loaded because running scripts is disabled`

Run this command:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Type `Y` when prompted, then try activating venv again.

### Still Not Working?

1. **Restart your computer** - Sometimes PATH updates need a restart
2. **Use full path to Python** - Find where Python installed and use full path
3. **Check installation** - Run: `Get-Command python` to see if it's found

---

## Quick Test Commands

After installation, test everything works:

```powershell
# 1. Check Python version
python --version

# 2. Navigate to project
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Test setup
python test_setup.py

# 5. Run bot once
python run.py --once
```

---

## Recommended: Method 1 (Microsoft Store)

**I recommend Method 1 (Microsoft Store)** because:
- ✅ Easiest installation
- ✅ Automatically adds to PATH
- ✅ Easy to update
- ✅ Works immediately

Just open Microsoft Store, search "Python 3.12", install, then close and reopen PowerShell!
