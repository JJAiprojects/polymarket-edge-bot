# GitHub Setup - Quick Guide

## Step 1: Verify Git is Installed

```powershell
git --version
```

You should see: `git version 2.x.x`

**If not found**, close and reopen PowerShell, then try again.

---

## Step 2: Configure Git (First Time Only)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 3: Initialize Repository

```powershell
cd C:\Users\jjwho\Documents\Cursor\Polymarket_EdgeDetectionBot
git init
```

---

## Step 4: Add Files

```powershell
git add .
```

---

## Step 5: Create First Commit

```powershell
git commit -m "Initial commit - Polymarket Edge Detection Bot"
```

---

## Step 6: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click **"New repository"** (or **+** icon)
3. Repository name: `polymarket-edge-bot`
4. Description: "AI bot for detecting edges on Polymarket"
5. Set to **Public** (or Private)
6. **DO NOT** check "Initialize with README" (we already have files)
7. Click **"Create repository"**

---

## Step 7: Connect and Push

GitHub will show you commands. Use these:

```powershell
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/polymarket-edge-bot.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be prompted for GitHub username and password (or token).

---

## Done! ✅

Your code is now on GitHub and ready for Render deployment!
