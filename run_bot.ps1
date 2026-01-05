# PowerShell script to run the bot with proper Python path
# This script finds Python and runs the bot

$pythonPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

if (Test-Path $pythonPath) {
    Write-Host "Found Python at: $pythonPath" -ForegroundColor Green
    Write-Host "Running bot..." -ForegroundColor Yellow
    & $pythonPath run.py $args
} else {
    Write-Host "Python not found at expected location." -ForegroundColor Red
    Write-Host "Trying to find Python..." -ForegroundColor Yellow
    
    # Try to find Python
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        Write-Host "Found Python: $($python.Source)" -ForegroundColor Green
        & python run.py $args
    } else {
        Write-Host "ERROR: Python not found!" -ForegroundColor Red
        Write-Host "Please install Python first. See INSTALL_PYTHON.md" -ForegroundColor Yellow
        exit 1
    }
}
