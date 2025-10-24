# Three-Stage Countdown Flow

## 🎯 Overview

The booking system now uses a **three-stage countdown** for maximum efficiency and accuracy when running hours in advance.

## 📊 Timeline Example (Target: 08:30:00)

```
05:30:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         │  Script starts
         │  🔧 System optimization checks
         │  ⏰ Times calculated:
         │     • Target: 08:30:00
         │     • Preparation phase: 07:30:00 (T-60 min)
         │     • Browser start: 08:20:00 (T-10 min)
         │
         ├─ 📅 STAGE 1: INITIAL COUNTDOWN
         │
         │  💤 Initial countdown: 180 minutes until preparation phase
         │  💤 Initial countdown: 160 minutes until preparation phase
         │  💤 Initial countdown: 140 minutes until preparation phase
         │  ...
         │
07:30:00 ├─ ⚡ ONE HOUR COUNTDOWN BEGINS!
         │
         ├─ ⏰ STAGE 2: PREPARATION PHASE ACTIVATED
         │
         │  💤 Waiting... 50 minutes until browser start
         │  💤 Waiting... 46 minutes until browser start
         │  ...
         │  💤 Waiting... 4 minutes until browser start
         │  💤 Waiting... 180s until browser start
         │  ⏳ 30.5s until browser start...
         │  ⏰ 5.2s until browser start...
         │
08:20:00 ├─ ⚡ BROWSER START TIME REACHED!
         │
         │  🌐 STARTING BROWSER AND LOGIN
         │  🌐 Starting browser...
         │  🔐 Logging in as username... (30s)
         │  🔑 Extracting CSRF token... (10s)
         │  🔥 Warming up network connection... (5s)
         │
08:20:45 ├─ ✅ STAGE 3: READY TO BOOK!
         │
         │  ⏳ Waiting... 555s until submission
         │  ⏳ Waiting... 545s until submission
         │  ...
         │  ⏳ 30.5s remaining...
         │  ⏰ 0.95s...
         │  🎯 Final countdown...
         │
08:30:00 ├─ ⚡ TIME REACHED! FIRING NOW!
         │  📊 Timing accuracy: +2.3ms from target
         │
         │  🚀 SUBMITTING BOOKING REQUEST (3 TIMES)...
         │  📤 Sending request #1/3...
         │  📤 Sending request #2/3...
         │  📤 Sending request #3/3...
         │
08:30:01 └─ ✅ BOOKING SUCCESSFUL!

```

## 🔄 Three Stages Explained

### **STAGE 1: Initial Countdown** (Script Start → T-60 min)

**Purpose**: Wait until we're 1 hour away from target time

**What happens**:
- Script performs system optimization checks
- Calculates all timing milestones
- Enters long wait mode with infrequent updates
- **NO browser activity** (saving resources)

**Console output**:
```
💤 Initial countdown: 180 minutes until preparation phase
💤 Initial countdown: 160 minutes until preparation phase
...
⚡ ONE HOUR COUNTDOWN BEGINS!
```

**Sleep intervals**:
- >40 min: 20-minute intervals (1200s)
- 20-40 min: 4-minute intervals (240s)
- 5-20 min: 1-minute intervals (60s)
- 1-5 min: 10-second intervals
- <1 min: 5-second intervals

**Skipped if**: You're already within 1 hour of target time

---

### **STAGE 2: Preparation Phase** (T-60 min → T-10 min)

**Purpose**: Countdown to browser start time

**What happens**:
- More frequent countdown updates
- Getting ready to launch browser
- **Still NO browser activity** (token stays fresh)

**Console output**:
```
💤 Waiting... 50 minutes until browser start
💤 Waiting... 30 minutes until browser start
...
⏰ 5.2s until browser start...
⚡ BROWSER START TIME REACHED!
```

**Sleep intervals**:
- >40 min: 20-minute intervals
- 20-40 min: 4-minute intervals
- 5-20 min: 1-minute intervals
- 1-5 min: 10-second intervals
- 10-60s: 5-second intervals
- <10s: 1-second intervals

**Then launches**:
- 🌐 Opens Playwright browser
- 🔐 Logs in (~30 seconds)
- 🔑 Extracts CSRF token (~10 seconds)
- 🔥 Pre-warms connection (~5 seconds)

**Total browser prep**: ~45-60 seconds

---

### **STAGE 3: Ready to Book** (T-10 min → Target Time)

**Purpose**: Final countdown with everything ready

**What happens**:
- Browser is open and authenticated
- CSRF token is fresh
- Network connection is warmed
- High-resolution timing active

**Console output**:
```
✅ STAGE 3: READY TO BOOK!
   Target: 2025-11-01 08:30:00 HKT
   Network offset: 100ms early

⏳ Waiting... 555s until submission
...
🎯 Final countdown...
⚡ TIME REACHED! FIRING NOW!
📊 Timing accuracy: +2.3ms from target
```

**Sleep intervals** (high precision):
- >60s: 10-second intervals
- 10-60s: 1-second intervals
- 1-10s: 0.5-second intervals
- 0.1-1s: 10ms intervals (high resolution)
- 10-100ms: 1ms intervals (very high resolution)
- <10ms: Busy-wait (maximum accuracy)

**Then submits**:
- 🚀 Fires 3 parallel requests
- 📊 Reports timing accuracy
- ✅ Shows booking result

---

## ⚙️ Configuration

In `master_booking.py`:

```python
PRE_TRIGGER_MINUTES = 10  # Browser opens 10 minutes before target (Stage 2→3)
```

**Recommendations**:
- **10 minutes** (default): Balanced, fresh tokens
- **15 minutes**: More buffer, slightly older tokens
- **5 minutes**: Aggressive, very fresh tokens (riskier)

**Note**: Stage 1 always activates at T-60 min (hardcoded, not configurable)

---

## 🎯 Key Features

### 1. **Intelligent Wait Detection**
```python
if now_hkt < one_hour_before:
    # Run Stage 1 initial countdown
else:
    # Skip to Stage 2 (already within 1 hour)
```

### 2. **Three Distinct Phases**
- **Stage 1**: Long wait (hours) - minimal updates
- **Stage 2**: Medium wait (50 min) - browser prep
- **Stage 3**: Short wait (10 min) - ready to fire

### 3. **Resource Efficiency**
- Browser closed during Stage 1 & 2
- Only opens at T-10 min
- Saves CPU, memory, and network

### 4. **Token Freshness**
- CSRF token extracted 10 minutes before
- Minimal chance of expiration
- More reliable authentication

---

## 📋 What You'll See

### If running 3 hours early (05:30 → 08:30):

```
🎯 GENERIC BOOKING SYSTEM - HIGH ACCURACY MODE
======================================================================

🔧 SYSTEM OPTIMIZATION
✅ System time synchronized (diff: 12ms)
⚡ Process priority boosted

⏰ Current time: 05:30:00 HKT
⏰ Target time: 08:30:00 HKT
⏰ Preparation phase starts: 07:30:00 HKT (T-60 min)
⏰ Browser start time: 08:20:00 HKT (T-10 min)
======================================================================

======================================================================
📅 STAGE 1: INITIAL COUNTDOWN
======================================================================
💤 Initial countdown: 120 minutes until preparation phase
[... 2 hours of waiting ...]
⚡ ONE HOUR COUNTDOWN BEGINS!

======================================================================
⏰ STAGE 2: PREPARATION PHASE ACTIVATED
======================================================================
💤 Waiting... 50 minutes until browser start
[... 50 minutes of waiting ...]
⚡ BROWSER START TIME REACHED!

======================================================================
🌐 STARTING BROWSER AND LOGIN
======================================================================
🌐 Starting browser...
🔐 Logging in...
✅ Login successful!
🔑 Extracting CSRF token...
✅ CSRF Token: abc123...
🔥 Warming up network connection...
✅ Connection warmed and ready

======================================================================
✅ STAGE 3: READY TO BOOK!
======================================================================
   Target: 2025-11-01 08:30:00 HKT
   Network offset: 100ms early
   Facility: Volleyball Court No. 3
   Time: 08:30 - 09:30
======================================================================

⏳ Waiting... 555s until submission
[... 9 minutes of waiting ...]
🎯 Final countdown...
⚡ TIME REACHED! FIRING NOW!
📊 Timing accuracy: +2.3ms from target

🚀 SUBMITTING BOOKING REQUEST (3 TIMES)...
✅ BOOKING SUCCESSFUL!
```

### If running 30 minutes early (08:00 → 08:30):

```
[System optimization checks...]

⏰ Current time: 08:00:00 HKT
⏰ Target time: 08:30:00 HKT
⏰ Preparation phase starts: 07:30:00 HKT (T-60 min)
⏰ Browser start time: 08:20:00 HKT (T-10 min)

======================================================================
⏰ Already within 1 hour of target - skipping initial countdown
======================================================================

💤 Waiting... 20 minutes until browser start
[... 20 minutes of waiting ...]
⚡ BROWSER START TIME REACHED!

[Continues with browser login and Stage 3...]
```

---

## 🚨 Important Notes

1. **Don't interrupt** during countdown - it's waiting on purpose
2. **Stage 1 is normal** - it's supposed to take hours
3. **Browser opens automatically** at T-10 min
4. **All timing is automatic** - no manual intervention needed
5. **Console updates are intentional** - less spam during long waits

---

## 💡 Pro Tips

1. **Start early**: 2-3 hours before target for maximum reliability
2. **Check initial output**: Verify all times are calculated correctly
3. **Trust the process**: Long waits are normal and expected
4. **Monitor Stage 3**: This is when accuracy matters most
5. **Review timing report**: Use it to tune network_offset_ms

---

## 🆘 Troubleshooting

| Situation | Expected Behavior |
|-----------|------------------|
| Script seems frozen | Normal - it's in long wait mode |
| No browser for hours | Correct - waits until T-10 min |
| Stage 1 skipped | You started within 1 hour of target |
| Updates every 20 min | Normal for Stage 1 (>40 min remaining) |
| Browser opens early | Check PRE_TRIGGER_MINUTES config |

---

**Summary**: The three-stage system ensures maximum efficiency for long-duration runs while maintaining accuracy when it matters most! 🎯
