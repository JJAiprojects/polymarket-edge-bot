# Fix: Terminal is Read-Only

## The Problem
Cursor's "Agent terminals" are read-only - you can't type or paste into them.

## The Solution: Create a NEW Terminal

### Method 1: Keyboard Shortcut (Fastest)
1. **Press**: `Ctrl + Shift + `` (backtick key, usually above Tab)
   - This creates a NEW terminal you can type in!

### Method 2: Menu
1. Click **Terminal** in the top menu
2. Select **New Terminal**
3. This creates a NEW terminal you can type in!

### Method 3: Right-Click
1. Right-click in the terminal area
2. Select **New Terminal**

---

## Once You Have a New Terminal:

1. **Navigate to your project:**
   ```
   cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
   ```

2. **Activate virtual environment:**
   ```
   .\venv\Scripts\Activate.ps1
   ```

3. **Run commands:**
   ```
   python run.py --once
   ```

---

## How to Tell the Difference:

- **Read-Only Terminal (Agent)**: Shows "Agent terminals are read-only" at bottom
- **Writable Terminal**: No such message, you can click and type in it

---

## Quick Tip:
Close the read-only agent terminal and create a new one using `Ctrl + Shift + ``
