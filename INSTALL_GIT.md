# Install Git on Windows

## Method 1: Using Winget (Easiest)

If you have winget (Windows Package Manager):

```powershell
winget install --id Git.Git -e --source winget
```

Then **restart your terminal** or refresh PATH:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

---

## Method 2: Download from Official Website

1. Go to: https://git-scm.com/download/win
2. Download the installer (64-bit)
3. Run the installer
4. **Important**: During installation, select:
   - ✅ "Add Git to PATH" option
   - ✅ "Use Git from the Windows Command Prompt"
5. Complete installation
6. **Restart your terminal/PowerShell**

---

## Method 3: Using Chocolatey (If Installed)

```powershell
choco install git
```

---

## Verify Installation

After installing, **close and reopen PowerShell**, then:

```powershell
git --version
```

You should see: `git version 2.x.x`

---

## After Installing Git

Once Git is installed, you can proceed with:

```powershell
git init
git add .
git commit -m "Initial commit"
```

---

## Quick Install Command

Run this in PowerShell (as Administrator if needed):

```powershell
winget install Git.Git
```

Then restart your terminal!
