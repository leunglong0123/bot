# Logging Guide

## Overview

All console output from the booking system is automatically saved to log files for review and debugging. This is especially useful for long-running sessions (3+ hours) where you can't monitor the console constantly.

## 🎯 Features

- **Dual Output**: Everything appears in both terminal AND log file
- **Automatic Timestamping**: Log files named with HKT date/time
- **Windows Compatible**: Uses `os.path.join()` for cross-platform paths
- **Per-Account Logs**: Each account gets its own log file
- **Master Log**: Main process has separate log file

## 📁 Log File Structure

```
bot/
├── logs/
│   ├── booking_log_20251101_053000_master.txt      # Master process
│   ├── booking_log_20251101_053001_420582.txt      # Account 1
│   ├── booking_log_20251101_053001_534610.txt      # Account 2
│   ├── booking_log_20251101_053001_420009.txt      # Account 3
│   └── ...
└── booking_run_20251101_053000/
    ├── debug_csrf_page_420582.html
    ├── booking_response_20251101_083000_123456_req1.html
    └── ...
```

## 📝 Log File Format

### Header
```
======================================================================
PolyU Booking System - Log File
======================================================================
Started: 2025-11-01 05:30:00 HKT
User ID: 420582
Log File: logs/booking_log_20251101_053000_420582.txt
======================================================================

```

### Body
All console output (everything you see in terminal is saved here)

### Footer
```
======================================================================
Log ended: 2025-11-01 08:30:15 HKT
======================================================================
```

## 🚀 How It Works

### Automatic (No Configuration Needed)

When you run `master_booking.py`:
1. **logs/** directory is created automatically
2. Each process gets unique log file based on HKT timestamp + user_id
3. All print statements go to both terminal and log file
4. Log file closes automatically when process completes

### What Gets Logged

**Everything visible in terminal:**
- ✅ System optimization checks
- ✅ All countdown messages
- ✅ Browser startup and login
- ✅ CSRF token extraction
- ✅ Network connection warming
- ✅ Final countdown and timing accuracy
- ✅ Booking submission results
- ✅ Error messages and warnings

## 🔍 Example Log Content

```log
======================================================================
PolyU Booking System - Log File
======================================================================
Started: 2025-11-01 05:30:00 HKT
User ID: 420582
Log File: logs/booking_log_20251101_053000_420582.txt
======================================================================

======================================================================
🎯 GENERIC BOOKING SYSTEM - HIGH ACCURACY MODE
======================================================================
Sport: VOLLEYBALL_SHAW
Time Slot: custom (08:30-09:30)
Date: 01 Nov 2025
Log file: logs/booking_log_20251101_053000_420582.txt
======================================================================

======================================================================
🔧 SYSTEM OPTIMIZATION
======================================================================
[05:30:00.123] 🕐 Checking system time synchronization...
[05:30:00.456] ✅ System time synchronized (diff: 12ms)
[05:30:00.789] ⚡ Process priority boosted (macOS)
======================================================================

⏰ Current time: 05:30:01 HKT
⏰ Target time: 08:30:00 HKT
⏰ Preparation phase starts: 07:30:00 HKT (T-60 min)
⏰ Browser start time: 08:20:00 HKT (T-10 min)
======================================================================

======================================================================
📅 STAGE 1: INITIAL COUNTDOWN
======================================================================
[05:30:01.234] 💤 Initial countdown: 120 minutes until preparation phase
[05:50:01.234] 💤 Initial countdown: 100 minutes until preparation phase
...
[07:30:00.000] ⚡ ONE HOUR COUNTDOWN BEGINS!

======================================================================
⏰ STAGE 2: PREPARATION PHASE ACTIVATED
======================================================================
[07:30:00.123] 💤 Waiting... 50 minutes until browser start
...
[08:20:00.000] ⚡ BROWSER START TIME REACHED!

======================================================================
🌐 STARTING BROWSER AND LOGIN
======================================================================
[08:20:00.123] 🌐 Starting browser...
[08:20:02.456] ✅ Browser started
[08:20:02.789] 🔐 Logging in as 17052989d...
[08:20:35.123] ✅ Login successful! (15 cookies)
[08:20:35.456] 🔑 Extracting CSRF token...
[08:20:48.789] ✅ CSRF Token: abc123-def456-...
[08:20:49.123] 🍪 Transferring cookies to requests session...
[08:20:49.456] ✅ Transferred 15 cookies
[08:20:49.789] 🔥 Warming up network connection...
[08:20:50.123] ✅ Connection warmed and ready

======================================================================
✅ STAGE 3: READY TO BOOK!
======================================================================
   Target: 2025-11-01 08:30:00 HKT
   Network offset: 100ms early
   Facility: Volleyball Court No. 3
   Time: 08:30 - 09:30
======================================================================

[08:20:50.456] ⏳ Waiting... 555s until submission
...
[08:29:59.900] 🎯 Final countdown...
[08:30:00.002] ⚡ TIME REACHED! FIRING NOW!
[08:30:00.002] 📊 Timing accuracy: +2.3ms from target

[08:30:00.002] 🚀 SUBMITTING BOOKING REQUEST (3 TIMES)...
[08:30:00.002]    Sport: volleyball_shaw
[08:30:00.002]    Facility: Volleyball Court No. 3
[08:30:00.002]    Time: 08:30 - 09:30
[08:30:00.003] 🚀 Sending all 3 requests in parallel...
[08:30:00.050] 📤 Sending request #1/3...
[08:30:00.051] 📤 Sending request #2/3...
[08:30:00.052] 📤 Sending request #3/3...
[08:30:00.200] 📬 Response #1 received in 150ms
[08:30:00.201] 📬 Response #2 received in 150ms
[08:30:00.202] 📬 Response #3 received in 150ms
[08:30:00.300] 💾 Saved response to booking_run_20251101_053000/...
[08:30:00.400] 📊 All 3 requests sent!
[08:30:00.400] ✅ BOOKING SUCCESSFUL!

======================================================================
📋 BOOKING PROCESS COMPLETE
======================================================================

[08:30:00.500] 🌐 Browser left open for inspection
[08:30:00.500] ⏸️  Process will stay alive to keep browser open...
[08:30:00.500] 💡 Press Ctrl+C to close all browsers and exit

======================================================================
Log ended: 2025-11-01 08:30:15 HKT
======================================================================
```

## 📊 Log File Usage

### Review After Completion

```bash
# View master log
cat logs/booking_log_*_master.txt

# View specific account log
cat logs/booking_log_*_420582.txt

# View all logs
cat logs/*.txt

# Search for errors across all logs
grep "❌" logs/*.txt

# Check timing accuracy
grep "Timing accuracy" logs/*.txt
```

### Monitor During Run (separate terminal)

```bash
# Tail master log (updates in real-time)
tail -f logs/booking_log_*_master.txt

# Tail specific account
tail -f logs/booking_log_*_420582.txt

# Watch for "BOOKING SUCCESSFUL"
tail -f logs/*.txt | grep "SUCCESSFUL"
```

### Windows PowerShell

```powershell
# View log
Get-Content logs\booking_log_*_master.txt

# Tail log (monitor in real-time)
Get-Content logs\booking_log_*_master.txt -Wait

# Search for errors
Select-String -Path logs\*.txt -Pattern "❌"
```

## 🛠️ Troubleshooting

### Log File Not Created

**Symptoms**: No files in `logs/` directory

**Causes**:
1. Permission issues
2. Disk full

**Solutions**:
```bash
# Check permissions
ls -la logs/

# Create directory manually
mkdir -p logs
chmod 755 logs

# Check disk space
df -h
```

### Log File Empty

**Symptoms**: Log file exists but has no content

**Causes**:
1. Process crashed immediately
2. Buffering not flushed

**Solutions**:
- Check terminal output for errors
- Log files auto-flush after each write
- If process crashes, partial log should still be saved

### Multiple Log Files for Same Run

**Normal Behavior**: Each account gets its own log file

```
booking_log_20251101_053000_master.txt    # Master process
booking_log_20251101_053001_420582.txt    # Account 1
booking_log_20251101_053001_534610.txt    # Account 2
```

This is intentional - makes it easy to review individual account activity.

## 💡 Pro Tips

### 1. Clean Up Old Logs

```bash
# Delete logs older than 7 days
find logs/ -name "*.txt" -mtime +7 -delete

# Archive logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/
rm -rf logs/*.txt
```

### 2. Monitor Multiple Accounts

```bash
# Open separate terminal for each account
terminal1$ tail -f logs/*_420582.txt
terminal2$ tail -f logs/*_534610.txt
terminal3$ tail -f logs/*_master.txt
```

### 3. Grep for Important Events

```bash
# Find all browser start times
grep "BROWSER START TIME REACHED" logs/*.txt

# Find all submission attempts
grep "FIRING NOW" logs/*.txt

# Find timing accuracy
grep "Timing accuracy" logs/*.txt

# Find errors only
grep -E "(❌|ERROR|Failed)" logs/*.txt
```

### 4. Compare Timing Across Accounts

```bash
# Extract submission times for all accounts
grep "TIME REACHED" logs/*.txt | sort
```

## 🔒 Security

- Log files saved in `logs/` directory (in `.gitignore`)
- Contains timestamps and account activity
- May contain user IDs (not passwords)
- Safe to share for debugging (no sensitive credentials)

**Important**: Logs do NOT contain:
- ❌ Passwords
- ❌ CSRF tokens (only shown as "abc123...")
- ❌ Session cookies
- ❌ Credit card info
- ❌ Personal data

## 📦 File Retention

**Recommended**:
- Keep logs for 30 days
- Archive important successful bookings
- Delete failed attempts after review

**Automatic Cleanup** (optional):

Add to crontab (macOS/Linux):
```bash
# Clean logs older than 30 days, daily at 2am
0 2 * * * find /path/to/bot/logs -name "*.txt" -mtime +30 -delete
```

Windows Task Scheduler:
```powershell
# PowerShell script: cleanup_logs.ps1
Get-ChildItem logs\*.txt | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

## 🎓 Summary

- ✅ Automatic logging - no configuration needed
- ✅ Dual output (terminal + file)
- ✅ Windows/macOS/Linux compatible paths
- ✅ Per-account log files for easy review
- ✅ Full session capture from start to finish
- ✅ Safe to share (no sensitive credentials)
- ✅ Easy to search and analyze
- ✅ Real-time monitoring with `tail -f`

Perfect for debugging issues, verifying timing accuracy, and reviewing long-running booking sessions! 📝
