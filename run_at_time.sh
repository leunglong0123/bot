#!/bin/bash

# Script to run master_booking.py at a specific time
# Target: 08:00:00 AM HKT on October 18, 2025

TARGET_TIME="2025-10-18 08:25:00"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "========================================"
echo "📅 Scheduled Booking Script"
echo "========================================"
echo "Target time: $TARGET_TIME HKT"
echo "Script location: $SCRIPT_DIR"
echo "Current time: $(TZ='Asia/Hong_Kong' date '+%Y-%m-%d %H:%M:%S') HKT"
echo ""

# Convert target time to epoch (seconds since 1970-01-01)
# On macOS, date command works differently
TARGET_EPOCH=$(TZ='Asia/Hong_Kong' date -j -f "%Y-%m-%d %H:%M:%S" "$TARGET_TIME" "+%s" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Error: Could not parse target time"
    exit 1
fi

# Get current time in epoch
CURRENT_EPOCH=$(date "+%s")

# Calculate seconds to wait
SECONDS_TO_WAIT=$((TARGET_EPOCH - CURRENT_EPOCH))

if [ $SECONDS_TO_WAIT -lt 0 ]; then
    echo "❌ Error: Target time has already passed!"
    echo "   Target: $TARGET_TIME"
    echo "   Current: $(TZ='Asia/Hong_Kong' date '+%Y-%m-%d %H:%M:%S')"
    exit 1
fi

# Convert seconds to human readable format
HOURS=$((SECONDS_TO_WAIT / 3600))
MINUTES=$(((SECONDS_TO_WAIT % 3600) / 60))
SECONDS=$((SECONDS_TO_WAIT % 60))

echo "⏰ Time until execution: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo "💤 Sleeping until target time..."
echo ""
echo "Press Ctrl+C to cancel"
echo ""

# Sleep until target time
sleep $SECONDS_TO_WAIT

echo ""
echo "========================================"
echo "🚀 TARGET TIME REACHED!"
echo "========================================"
echo "Current time: $(TZ='Asia/Hong_Kong' date '+%Y-%m-%d %H:%M:%S') HKT"
echo ""
echo "🔥 Starting master_booking.py..."
echo "========================================"
echo ""

# Change to script directory and run Python script
cd "$SCRIPT_DIR"

# Use specific Python interpreter
PYTHON_PATH="/Users/kalongleung/.pyenv/shims/python"

echo "Using Python: $PYTHON_PATH"
echo ""

# Run the Python script
$PYTHON_PATH master_booking.py

echo ""
echo "========================================"
echo "✅ Script completed!"
echo "Finished at: $(TZ='Asia/Hong_Kong' date '+%Y-%m-%d %H:%M:%S') HKT"
echo "========================================"

