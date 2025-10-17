"""
Booking configuration for different sports
"""

# Login credentials
USERNAME = "username"
PASSWORD = "password"
USER_ID = "442240"

# Common venue
CENTER_ID = "1"
CENTER_NAME = "Shaw Sports Complex"
DATASET_ID = "18"

# Sport-specific configurations
SPORTS_CONFIG = {
    "volleyball": {
        "activity_id": "6",
        "facility_id": "1751",
        "facility_name": "Volleyball Court No. 3",
    },
    "table_tennis": {
        "activity_id": "11",
        "facility_id": "16",
        "facility_name": "Table Tennis Table No. 1",
    }
}

# Time slots configuration (you can add more)
TIME_SLOTS = {
    "morning_early": {
        "start": "08:30",
        "end": "09:30"
    },
    "morning_mid": {
        "start": "09:30",
        "end": "10:30"
    },
    "morning_late": {
        "start": "10:30",
        "end": "11:30"
    },
    "noon": {
        "start": "11:30",
        "end": "12:30"
    },
    "afternoon_early": {
        "start": "12:30",
        "end": "13:30"
    },
    # Add more slots as needed
}


def get_booking_config(sport, time_slot, booking_date):
    """
    Generate booking configuration for a specific sport and time slot

    Args:
        sport: "volleyball" or "table_tennis"
        time_slot: Key from TIME_SLOTS (e.g., "morning_early")
        booking_date: Date string (e.g., "25 Oct 2025")

    Returns:
        dict: Complete booking configuration
    """
    if sport not in SPORTS_CONFIG:
        raise ValueError(f"Invalid sport: {sport}. Choose from {list(SPORTS_CONFIG.keys())}")

    if time_slot not in TIME_SLOTS:
        raise ValueError(f"Invalid time slot: {time_slot}. Choose from {list(TIME_SLOTS.keys())}")

    sport_config = SPORTS_CONFIG[sport]
    slot_config = TIME_SLOTS[time_slot]

    return {
        "username": USERNAME,
        "password": PASSWORD,
        "user_id": USER_ID,
        "sport": sport,
        "activity_id": sport_config["activity_id"],
        "facility_id": sport_config["facility_id"],
        "facility_name": sport_config["facility_name"],
        "center_id": CENTER_ID,
        "center_name": CENTER_NAME,
        "dataset_id": DATASET_ID,
        "date": booking_date,
        "start_time": slot_config["start"],
        "end_time": slot_config["end"],
    }
