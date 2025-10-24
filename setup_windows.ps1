# PowerShell Setup Script for PolyU Booking Bot
# This script sets up the Python environment and installs all dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PolyU Booking Bot - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# [1/5] Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
if (-not (Test-CommandExists python)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# [2/5] Check Python version
Write-Host "[2/5] Verifying Python version..." -ForegroundColor Yellow
$versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python 3.9 or higher is required" -ForegroundColor Red
    Write-Host "Please upgrade Python from https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Python version is compatible!" -ForegroundColor Green
Write-Host ""

# [3/5] Upgrade pip
Write-Host "[3/5] Upgrading pip..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip | Out-Null
    Write-Host "pip upgraded successfully!" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# [4/5] Install dependencies
Write-Host "[4/5] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# [5/5] Install Playwright browsers
Write-Host "[5/5] Installing Playwright browsers..." -ForegroundColor Yellow
Write-Host "This may take several minutes on first run..." -ForegroundColor Gray
python -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Playwright browsers" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Playwright browsers installed successfully!" -ForegroundColor Green
Write-Host ""

# Create accounts.csv template if it doesn't exist
if (-not (Test-Path "accounts.csv")) {
    Write-Host "Creating accounts.csv template..." -ForegroundColor Yellow
    $csvContent = @"
name,username,password,user_id
Account1,your_username1,your_password1,user_id1
Account2,your_username2,your_password2,user_id2
"@
    $csvContent | Out-File -FilePath "accounts.csv" -Encoding UTF8
    Write-Host "Template created! Please edit accounts.csv with your credentials." -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit accounts.csv with your account credentials"
Write-Host "2. Review master_booking.py configuration (SPORT, DATE, TIME)"
Write-Host "3. Run: python master_booking.py"
Write-Host ""
Write-Host "For more information, see SETUP_WINDOWS.md" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
