# Windows Setup Guide - PolyU Booking Bot

This guide will help you set up the booking bot on Windows.

## Prerequisites

- Windows 10 or Windows 11
- Administrator access (for installing software)
- Internet connection

## Quick Setup (Recommended)

### Option 1: Batch Script (Easiest)

1. **Download or clone this repository** to your computer

2. **Open Command Prompt** in the project folder:
   - Press `Win + R`
   - Type `cmd` and press Enter
   - Navigate to the project folder using `cd` command
   - Or right-click the folder and select "Open in Terminal"

3. **Run the setup script**:
   ```cmd
   setup_windows.bat
   ```

4. **Follow the prompts** - the script will:
   - Check Python installation
   - Install all dependencies
   - Install Playwright browsers
   - Create an accounts.csv template

### Option 2: PowerShell Script (Alternative)

1. **Open PowerShell** in the project folder:
   - Right-click the folder while holding Shift
   - Select "Open PowerShell window here"

2. **Allow script execution** (first time only):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Run the setup script**:
   ```powershell
   .\setup_windows.ps1
   ```

## Manual Setup

If the automated scripts don't work, follow these steps:

### Step 1: Install Python

1. Download Python 3.9 or higher from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Install Dependencies

1. Open Command Prompt in the project folder
2. Upgrade pip:
   ```cmd
   python -m pip install --upgrade pip
   ```

3. Install requirements:
   ```cmd
   pip install -r requirements.txt
   ```

### Step 3: Install Playwright Browsers

```cmd
python -m playwright install chromium
```

### Step 4: Create accounts.csv

Create a file named `accounts.csv` with your account information:

```csv
name,username,password,user_id
Account1,your_username1,your_password1,user_id1
Account2,your_username2,your_password2,user_id2
```

## Configuration

### Edit master_booking.py

Open `master_booking.py` and configure these variables:

```python
SPORT = "volleyball_shaw"  # Your desired sport
TARGET_TIME = '08:30:00'   # When to submit bookings
START_TIME = "08:30"       # Time slot start
END_TIME = "12:30"         # Time slot end
DATE = "01 Nov 2025"       # Booking date
```

### Available Sports

- `volleyball_shaw` - Shaw Volleyball Court
- `volleyball_practice_hall` - Practice Hall
- `volleyball_fsch` - FSCH Volleyball Court
- `table_tennis` - Table Tennis

## Running the Bot

### Standard Run (with visible browsers)

```cmd
python master_booking.py
```

### Headless Mode (hidden browsers)

Edit `master_booking.py` and set `headless=True` in the function call:

```python
run_parallel_bookings(
    # ... other parameters ...
    headless=True  # Change this to True
)
```

## Troubleshooting

### Python not found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Reinstall Python and check "Add Python to PATH"
2. Or add Python manually to PATH:
   - Search for "Environment Variables" in Windows
   - Edit PATH and add Python installation directory (e.g., `C:\Python39\`)

### Permission Denied

**Error**: Scripts are disabled on this system

**Solution** (PowerShell only):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Playwright Installation Failed

**Solution**:
```cmd
python -m playwright install --force chromium
```

### Module Not Found Errors

**Error**: `ModuleNotFoundError: No module named 'playwright'`

**Solution**:
```cmd
pip install -r requirements.txt --force-reinstall
```

### Multiple Browser Windows

The bot launches one browser per account. Ensure your system has enough resources:
- **Recommended**: 8GB+ RAM for 5+ accounts
- **Minimum**: 4GB RAM for 2-3 accounts

To reduce resource usage, enable headless mode.

### Firewall Warnings

Windows may show firewall warnings for Python/Playwright. Click "Allow access" to permit network connections.

## System Requirements

### Minimum
- Windows 10 (64-bit)
- Python 3.9+
- 4GB RAM
- 2GB free disk space
- Stable internet connection

### Recommended
- Windows 11 (64-bit)
- Python 3.11+
- 8GB+ RAM
- 5GB free disk space
- Fast internet connection (50+ Mbps)

## Important Notes

### Timing Accuracy

- The bot compensates for network delay (configured as `network_offset_ms`)
- Test with a non-critical booking first to verify timing
- Adjust `network_offset_ms` based on your network speed

### Account Safety

- Keep `accounts.csv` secure and private
- Never commit it to version control
- It's already in `.gitignore` for safety

### Multiple Accounts

- Each account runs in a separate process
- All accounts submit at the same target time
- Slots are automatically distributed across the time range

## Output Files

The bot creates a timestamped folder for each run:
```
booking_run_YYYYMMDD_HHMMSS/
├── debug_user1.html
├── debug_user2.html
└── ...
```

These files help diagnose issues if bookings fail.

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in the console
3. Check output HTML files for debugging
4. Verify your network connection and credentials

## License

This tool is for educational purposes. Use responsibly and in accordance with your institution's policies.
