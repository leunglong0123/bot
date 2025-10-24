# Quick Start Guide - High Accuracy Mode

## 🚀 Quick Setup (3-Hour Advance Run)

### Step 1: System Prep (5 minutes before running)

```bash
# 1. Close unnecessary applications
# 2. Connect to AC power
# 3. Disable sleep mode
# 4. Use wired internet (if possible)
```

### Step 2: Configure Your Booking

Edit `master_booking.py`:

```python
SPORT = "volleyball_shaw"        # Your sport
TARGET_TIME = '08:30:00'         # When to submit (HH:MM:SS)
START_TIME = "08:30"             # Slot start time
END_TIME = "12:30"               # Slot end time
DATE = "01 Nov 2025"             # Booking date
PRE_TRIGGER_MINUTES = 15         # Browser opens 15 min before
```

Edit `accounts.csv`:
```csv
name,username,password,user_id
YourName,your_username,your_password,your_user_id
```

### Step 3: Run the Script

```bash
# Normal run
python master_booking.py

# For best accuracy (recommended)
sudo python master_booking.py  # macOS/Linux
# OR
# Run as Administrator (Windows)
```

### Step 4: Monitor Output

You should see:
```
🔧 SYSTEM OPTIMIZATION
🕐 Checking system time synchronization...
✅ System time synchronized (diff: 12ms)
⚡ Process priority boosted

⏰ Current time: 05:30:00 HKT
⏰ Target time: 08:30:00 HKT
⏰ Browser start time: 08:15:00 HKT (T-15 min)

💤 Waiting... 165 minutes until browser start
```

### Step 5: Wait for Completion

The script will automatically:
- Wait until 08:15:00 (T-15min)
- Open browser and login
- Get CSRF token
- Pre-warm connection
- Wait until 08:30:00
- Submit booking with high accuracy
- Report timing accuracy

### Step 6: Check Results

Look for:
```
⚡ TIME REACHED! FIRING NOW!
📊 Timing accuracy: +2.3ms from target
📤 Sending request #1/3...
📤 Sending request #2/3...
📤 Sending request #3/3...
✅ BOOKING SUCCESSFUL!
```

## ⚙️ Quick Tuning

### If consistently LATE by X ms:
```python
network_offset_ms=100 + X,  # Increase offset
```

### If consistently EARLY by X ms:
```python
network_offset_ms=100 - X,  # Decrease offset
```

### If browser opens too early:
```python
PRE_TRIGGER_MINUTES = 10  # Reduce to 10 minutes
```

### If token expires:
```python
PRE_TRIGGER_MINUTES = 20  # Increase to 20 minutes
```

## 📊 What's Different in High Accuracy Mode?

### OLD BEHAVIOR:
- Opens browser immediately when script starts
- Basic timing (less accurate)
- No system optimization
- No connection pre-warming

### NEW BEHAVIOR:
- ✅ Checks system time synchronization
- ✅ Boosts process priority
- ✅ Waits until T-15min to open browser
- ✅ Pre-warms network connection
- ✅ High-resolution timing (sub-millisecond)
- ✅ Reports actual timing accuracy
- ✅ Adaptive sleep intervals
- ✅ Busy-wait in final 10ms

## 🎯 Expected Timeline (3-Hour Example)

```
05:30:00 - Script starts
           System optimization checks
           💤 Waiting...

08:15:00 - PRE-TRIGGER TIME REACHED
           🌐 Opens browser
           🔐 Logs in (30s)
           🔑 Gets CSRF token (10s)
           🔥 Warms connection (5s)
           ✅ Ready to book
           ⏳ Waiting for target time...

08:29:50 - Final countdown begins
           🎯 High-resolution timing active

08:30:00.002 - ⚡ FIRES REQUEST
           📊 Timing accuracy: +2ms
           🚀 Submits booking (3x parallel)

08:30:01 - ✅ Booking complete
           📁 Saves response files
           🌐 Browser stays open for inspection
```

## 🚨 Important Notes

1. **DO NOT** close terminal/command prompt
2. **DO NOT** put computer to sleep
3. **DO NOT** disconnect from internet
4. **DO NOT** run other heavy applications
5. **DO** keep computer plugged in
6. **DO** use wired connection if possible

## 📱 Quick Checklist

Before running:
- [ ] Accounts.csv updated
- [ ] Sport/date/time configured
- [ ] Computer plugged in
- [ ] Sleep mode disabled
- [ ] Wired internet (or strong WiFi)
- [ ] Unnecessary apps closed
- [ ] System time synchronized

After running:
- [ ] See "System time synchronized" message
- [ ] See "Process priority boosted" message
- [ ] See countdown to browser start
- [ ] Browser opens at correct time
- [ ] See "READY TO BOOK" message
- [ ] See timing accuracy report
- [ ] Check response HTML files

## 🆘 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| "Could not boost priority" | Run as admin/sudo |
| "System time off by X seconds" | Sync your system clock |
| "Connection warm-up failed" | Check internet connection |
| Always late by X ms | Increase network_offset_ms by X |
| Always early by X ms | Decrease network_offset_ms by X |
| Browser never opens | Check pre_trigger_minutes config |
| Script hangs at countdown | Normal - it's waiting |

## 💡 Pro Tips

1. **Test run first**: Do a test with a non-critical booking to verify timing
2. **Check logs**: Response HTML files saved in `booking_run_TIMESTAMP/` folder
3. **Multiple accounts**: All accounts fire at same time (parallel)
4. **Timing report**: Use the accuracy report to tune network_offset_ms
5. **Stay calm**: Script handles everything automatically after you start it

## 📚 More Info

- See `ACCURACY_GUIDE.md` for detailed technical information
- See `SETUP_WINDOWS.md` for Windows installation
- See `master_booking.py` for configuration options

---

**Good luck! Your booking system is now optimized for maximum accuracy! 🎯**
