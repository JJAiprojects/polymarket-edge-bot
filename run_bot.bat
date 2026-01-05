@echo off
REM Batch script to run the bot - works even if Python not in PATH

set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

if exist "%PYTHON_PATH%" (
    echo Found Python at: %PYTHON_PATH%
    echo Running bot...
    "%PYTHON_PATH%" run.py %*
) else (
    echo Python not found at expected location.
    echo Trying python command...
    python run.py %*
    if errorlevel 1 (
        echo.
        echo ERROR: Python not found!
        echo Please install Python first. See INSTALL_PYTHON.md
        pause
        exit /b 1
    )
)
