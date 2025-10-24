@echo off
REM Windows Setup Script for PolyU Booking Bot
REM This script sets up the Python environment and installs all dependencies

echo ========================================
echo PolyU Booking Bot - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check Python version (requires Python 3.9+)
echo [2/5] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.9 or higher is required
    echo Please upgrade Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python version is compatible!
echo.

REM Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)
echo.

REM Install dependencies
echo [4/5] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

REM Install Playwright browsers
echo [5/5] Installing Playwright browsers...
echo This may take several minutes on first run...
python -m playwright install chromium
if errorlevel 1 (
    echo ERROR: Failed to install Playwright browsers
    pause
    exit /b 1
)
echo Playwright browsers installed successfully!
echo.

REM Create accounts.csv template if it doesn't exist
if not exist accounts.csv (
    echo Creating accounts.csv template...
    echo name,username,password,user_id > accounts.csv
    echo Account1,your_username1,your_password1,user_id1 >> accounts.csv
    echo Account2,your_username2,your_password2,user_id2 >> accounts.csv
    echo Template created! Please edit accounts.csv with your credentials.
    echo.
)

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit accounts.csv with your account credentials
echo 2. Review master_booking.py configuration (SPORT, DATE, TIME)
echo 3. Run: python master_booking.py
echo.
echo For more information, see SETUP_WINDOWS.md
echo.
pause
