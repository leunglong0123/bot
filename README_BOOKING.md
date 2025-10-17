# Generic Booking System

Automated booking system for PolyU sports facilities with precise timing control.

## Features

- ✅ Pre-login to prepare session ahead of time
- ✅ Auto-extract CSRF token
- ✅ Submit at exact millisecond (with network latency compensation)
- ✅ Support multiple sports (volleyball, table tennis)
- ✅ Configurable time slots
- ✅ No browser/Selenium needed (direct HTTP requests)

## Installation

```bash
pip install requests beautifulsoup4 pytz
```

## Quick Start

### Option 1: Use Example Scripts

```bash
# Edit example_booking.py and uncomment the booking you want
python example_booking.py
```

### Option 2: Simple One-liner

```python
from book import GenericBooking

booking = GenericBooking()
booking.run(
    sport="volleyball",           # or "table_tennis"
    time_slot="morning_early",    # see available slots below
    booking_date="25 Oct 2025",
    target_time_str="08:30:00",   # Submit at exactly 8:30:00 AM HKT
    network_offset_ms=200         # Send 200ms early (network latency)
)
```

## Configuration

### 1. Available Sports

Edit `booking_config.py` (line 14-24):

```python
SPORTS_CONFIG = {
    "volleyball": {
        "facility_id": "1751",
        "facility_name": "Volleyball Court No. 3",
    },
    "table_tennis": {
        "facility_id": "16",
        "facility_name": "Table Tennis Table No. 1",
    }
}
```

### 2. Available Time Slots

Edit `booking_config.py` (line 27-44):

```python
TIME_SLOTS = {
    "morning_early":     { "start": "08:30", "end": "09:30" },
    "morning_mid":       { "start": "09:30", "end": "10:30" },
    "morning_late":      { "start": "10:30", "end": "11:30" },
    "noon":              { "start": "11:30", "end": "12:30" },
    "afternoon_early":   { "start": "12:30", "end": "13:30" },
    # Add more as needed
}
```

### 3. Login Credentials

Edit `booking_config.py` (line 7-9):

```python
USERNAME = "your_username"
PASSWORD = "your_password"
USER_ID = "your_user_id"
```

## How It Works

### Timeline Example (Target: 8:30:00 AM)

```
8:25:00 AM → Login
8:25:01 AM → Extract CSRF token
8:25:02 AM → ✅ Ready! Waiting...
8:29:50 AM → ⏳ 10 seconds remaining
8:29:59 AM → ⏰ 1.0 seconds
8:29:59.800 AM → ⚡ Firing request (200ms early for network latency)
8:30:00.105 AM → 📬 Response received
```

## Network Latency Compensation

The system sends requests slightly early to compensate for network delay:

```python
network_offset_ms=200  # Send 200ms early
```

- `200ms` = Default (good for most networks)
- `100ms` = Fast/local network
- `300ms` = Slower network or want extra buffer

## Testing

Test with a booking in 1 minute:

```python
python example_booking.py
# Then uncomment: test_booking_soon()
```

## File Structure

```
bot/
├── booking_config.py       # Main configuration (sports, slots, credentials)
├── book.py                 # Generic booking engine
├── example_booking.py      # Example usage scripts
├── events/
│   ├── volleyball-shaw.py  # Legacy volleyball config
│   └── table-tennis.py     # Legacy table tennis config
└── README_BOOKING.md       # This file
```

## Examples

### Book volleyball at 8:30 AM

```python
from book import GenericBooking

booking = GenericBooking()
booking.run(
    sport="volleyball",
    time_slot="morning_early",
    booking_date="25 Oct 2025",
    target_time_str="08:30:00",
    network_offset_ms=200
)
```

### Book table tennis at 9:30 AM

```python
booking = GenericBooking()
booking.run(
    sport="table_tennis",
    time_slot="morning_mid",
    booking_date="25 Oct 2025",
    target_time_str="08:30:00",  # Still submit at 8:30
    network_offset_ms=200
)
```

### Multiple bookings (different time slots)

```python
# Book 3 consecutive volleyball slots
for slot in ["morning_early", "morning_mid", "morning_late"]:
    booking = GenericBooking()
    booking.run(
        sport="volleyball",
        time_slot=slot,
        booking_date="25 Oct 2025",
        target_time_str="08:30:00",
        network_offset_ms=200
    )
```

## Tips

1. **Run 5 minutes early**: Start the script at 8:25 AM for an 8:30 AM submission
2. **Network offset**: Adjust based on your internet speed
3. **Test first**: Use `test_booking_soon()` to verify everything works
4. **Check response**: Look for "✅ BOOKING SUCCESSFUL!" in output

## Troubleshooting

### Login fails
- Check credentials in `booking_config.py`
- Verify PolyU website is accessible

### CSRF token not found
- Website structure may have changed
- Check if you're logged in successfully

### Booking submitted but failed
- Time slot may be already booked
- Check eligibility/quota limits
- Verify facility ID is correct
