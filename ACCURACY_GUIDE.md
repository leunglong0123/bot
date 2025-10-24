# High Accuracy Timing Guide

## Overview

Your booking system now includes advanced timing features to ensure maximum accuracy when submitting requests at the exact target time. This is crucial when running the script hours in advance.

## 🎯 Key Accuracy Features

### 1. **High-Resolution Timing**
- **Adaptive Sleep**: Uses different sleep intervals based on remaining time
  - `>60s`: 10s sleep intervals
  - `10-60s`: 1s sleep intervals
  - `1-10s`: 0.5s sleep intervals
  - `0.1-1s`: 10ms sleep intervals (high resolution)
  - `10-100ms`: 1ms sleep intervals (very high resolution)
  - `<10ms`: Busy-wait loop (maximum accuracy)

- **Timing Accuracy Report**: After submission, shows actual timing error
  ```
  📊 Timing accuracy: +2.3ms from target
  ```

### 2. **Process Priority Boosting**
Automatically boosts the process priority so the OS scheduler gives it higher priority:
- **Windows**: HIGH_PRIORITY_CLASS
- **macOS/Linux**: Nice value -10

**Benefits**:
- Reduces scheduling delays
- Minimizes time between wake-up and execution
- More consistent timing

**Note**: On macOS/Linux, you may need to run with elevated privileges for best results:
```bash
sudo python master_booking.py
```

### 3. **System Time Synchronization Check**
Verifies your system clock is synchronized with NTP servers (time.google.com):
- Checks time difference against authoritative time server
- Warns if system time is off by >1 second
- Reports synchronization accuracy in milliseconds

**Example Output**:
```
✅ System time synchronized (diff: 12ms)
```

**If you see warnings**:
- **Windows**: Settings → Time & Language → Sync now
- **macOS**: System Preferences → Date & Time → Enable "Set time automatically"
- **Linux**: `sudo ntpdate time.google.com` or enable `systemd-timesyncd`

### 4. **Network Connection Pre-warming**
Establishes TCP connection to the booking server before submission time:
- Reduces first-request latency
- Pre-resolves DNS
- Establishes TLS handshake
- Warms up connection pooling

**Timing**: Done after login, before waiting for target time

### 5. **Delayed Browser Initialization**
Browser only opens at pre-trigger time (default: 15 minutes before):
- Reduces resource usage
- Fresher CSRF tokens
- Less chance of session timeout
- More reliable connections

## ⚙️ Configuration

### Pre-Trigger Time
Located in `master_booking.py` line 180:

```python
PRE_TRIGGER_MINUTES = 15  # Start browser X minutes before target time
```

**Recommendations**:
- **High reliability**: 15-20 minutes (default)
- **Balanced**: 10-15 minutes
- **Aggressive**: 5-10 minutes (riskier, tokens may expire)

### Network Offset
Located in `master_booking.py` line 192:

```python
network_offset_ms=100,  # Send request this many ms early
```

**How to calibrate**:
1. Run a test booking and check timing accuracy report
2. If consistently late by X ms, increase offset by X
3. If consistently early by X ms, decrease offset by X

**Typical values**:
- **Fast connection**: 50-100ms
- **Average connection**: 100-200ms (default: 100ms)
- **Slow connection**: 200-500ms

## 🚀 Best Practices for 3-Hour Advance Run

### 1. System Preparation

**Close unnecessary applications**:
- Web browsers (except the booking one)
- Video streaming
- Downloads
- Background updates

**Keep running**:
- Your booking script only
- Essential system services

### 2. Network Stability

**Use wired connection** (recommended):
- More stable than WiFi
- Lower latency
- Less packet loss

**If using WiFi**:
- Stay close to router
- Use 5GHz band if available
- Avoid network congestion (torrents, streaming, etc.)

### 3. Power Management

**Disable sleep/hibernation**:

**Windows**:
```
Settings → System → Power & Sleep → Screen: Never, Sleep: Never
```

**macOS**:
```
System Preferences → Energy Saver → Prevent computer from sleeping: Checked
```

**Linux**:
```bash
sudo systemctl mask sleep.target suspend.target
```

**Use AC power** (not battery):
- Prevents performance throttling
- Ensures system stays awake

### 4. Time Synchronization

**Verify before running** (especially for 3-hour runs):

**Windows**:
```cmd
w32tm /query /status
```

**macOS**:
```bash
sudo sntp -sS time.apple.com
```

**Linux**:
```bash
timedatectl status
```

### 5. Running the Script

**Recommended approach**:

1. **Start 3 hours early**:
   ```bash
   python master_booking.py
   ```

2. **Monitor initial output**:
   - Check time sync status
   - Verify process priority boost
   - Note current/target/browser-start times

3. **Let it run unattended**:
   - The script will wait automatically
   - Browser opens at pre-trigger time (T-15min)
   - Submits at exact target time

4. **Check results**:
   - Look for timing accuracy report
   - Review HTML response files
   - Check browser for confirmation

## 📊 Understanding Timing Output

### During Wait Phase
```
💤 Waiting... 180 minutes until browser start
💤 Waiting... 120 minutes until browser start
...
⏰ 10.5s until browser start...
⚡ PRE-TRIGGER TIME REACHED!
```

### During Browser Phase
```
🌐 Starting browser...
🔐 Logging in...
🔑 Extracting CSRF token...
🔥 Warming up network connection...
```

### During Submission Phase
```
⏳ Waiting... 300s until submission
⏳ 30.5s remaining...
⏰ 0.95s...
🎯 Final countdown...
⚡ TIME REACHED! FIRING NOW!
📊 Timing accuracy: +1.8ms from target
```

## 🔍 Troubleshooting

### Issue: Timing consistently off by >50ms

**Causes**:
- System overload
- Network latency
- Incorrect network_offset_ms

**Solutions**:
1. Close more applications
2. Adjust `network_offset_ms` in master_booking.py
3. Run with elevated privileges (sudo/admin)

### Issue: "Could not verify time sync"

**Causes**:
- Firewall blocking NTP
- Network issues
- No internet connection

**Solutions**:
1. Check internet connection
2. Allow UDP port 123 through firewall
3. Manually sync system time

### Issue: "Could not boost priority"

**Causes**:
- Insufficient permissions
- psutil not installed

**Solutions**:
1. Run as admin/sudo
2. Install: `pip install psutil`
3. Script will still work, just less accurate

### Issue: Browser opens too early/late

**Cause**:
- PRE_TRIGGER_MINUTES misconfigured

**Solution**:
- Adjust PRE_TRIGGER_MINUTES in master_booking.py

## 📈 Expected Accuracy

With all optimizations enabled:

| Condition | Expected Accuracy |
|-----------|------------------|
| Ideal (wired, admin, no load) | ±1-5ms |
| Good (wired, normal user) | ±5-20ms |
| Average (WiFi, background tasks) | ±20-50ms |
| Poor (WiFi, high load) | ±50-200ms |

**Note**: Accuracy also depends on network latency to the booking server.

## 🎓 Technical Details

### Why Busy-Wait in Final 10ms?

Traditional `time.sleep()` has variable wake-up time due to OS scheduler:
- Sleep can wake up 1-15ms late on Windows
- Sleep can wake up 1-10ms late on macOS/Linux

Busy-waiting (continuous checking without sleep) in the final 10ms:
- Guarantees sub-millisecond accuracy
- CPU usage spikes briefly (acceptable for 10ms)
- Only CPU-intensive for <10ms before target

### Why Multiple Sleep Intervals?

Different intervals optimize for different scenarios:
- Long waits: Save CPU with longer sleeps
- Medium waits: Balance accuracy and CPU
- Short waits: Prioritize accuracy over CPU
- Final moment: Maximum accuracy (busy-wait)

### Why Pre-warm Connection?

First request typically takes longer due to:
- DNS resolution: 10-100ms
- TCP handshake: 20-100ms (RTT-dependent)
- TLS handshake: 50-200ms
- Connection pool initialization: 10-50ms

Pre-warming eliminates these delays, ensuring the submission request is as fast as possible.

## 🔐 Security Notes

- `psutil` is used only to boost process priority
- NTP check connects to time.google.com (Google's public NTP)
- No sensitive data is sent during optimization checks
- All network activity is to PolyU servers or trusted time servers

## 📝 Summary

For best results when running 3 hours in advance:

1. ✅ Use wired internet connection
2. ✅ Disable sleep/hibernation
3. ✅ Close unnecessary applications
4. ✅ Verify time synchronization
5. ✅ Run with admin/sudo if possible
6. ✅ Configure network_offset_ms based on your connection
7. ✅ Let script run unattended
8. ✅ Check timing accuracy report after submission

Good luck with your bookings! 🎯
