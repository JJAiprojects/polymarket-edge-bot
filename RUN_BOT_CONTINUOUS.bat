@echo off
REM Run bot continuously - double-click this file!

echo ========================================
echo Polymarket Edge Detection Bot
echo Running Continuously (every 15 minutes)
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in PATH. Trying full path...
    set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    if not exist "%PYTHON_PATH%" (
        echo ERROR: Python not found!
        echo Please install Python first.
        pause
        exit /b 1
    )
) else (
    set PYTHON_PATH=python
)

echo Using Python: %PYTHON_PATH%
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo.
echo Starting bot...
echo ========================================
echo.

REM Run the bot continuously
%PYTHON_PATH% run.py

pause
