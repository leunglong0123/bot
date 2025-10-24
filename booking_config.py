"""
Booking configuration for different sports
"""

# Login credentials
USERNAME = "123d"
PASSWORD = "abc"
USER_ID = "442240"

# Common venue
CENTER_ID = "51"
CENTER_NAME = "Shaw Sports Complex - Sports Practice Hall"
DATASET_ID = "18"

# Sport-specific configurations
SPORTS_CONFIG = {
    "volleyball": {
        "activity_id": "6",
        "facility_id": "8",
        "facility_name": "Volleyball Court No. 1",
    },
    "table_tennis": {
        "activity_id": "11",
        "facility_id": "16",
        "facility_name": "Table Tennis Table No. 1",
    },
    "fsch": {
        "activity_id": "6",
        "facility_id": "27",
        "facility_name": "Volleyball Court No. 2",
        "center_id": "2",
        "center_name": "Fong Shu Chuen Hall",
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


def get_booking_config(sport, time_slot, booking_date, custom_start_time=None, custom_end_time=None):
    """
    Generate booking configuration for a specific sport and time slot

    Args:
        sport: "volleyball" or "table_tennis"
        time_slot: Key from TIME_SLOTS (e.g., "morning_early") or None if using custom times
        booking_date: Date string (e.g., "25 Oct 2025")
        custom_start_time: Optional custom start time (overrides time_slot)
        custom_end_time: Optional custom end time (overrides time_slot)

    Returns:
        dict: Complete booking configuration
    """
    if sport not in SPORTS_CONFIG:
        raise ValueError(f"Invalid sport: {sport}. Choose from {list(SPORTS_CONFIG.keys())}")

    # Allow None time_slot if custom times are provided
    if time_slot is None and (custom_start_time is None or custom_end_time is None):
        raise ValueError(f"Either time_slot or both custom times must be provided")

    if time_slot is not None and time_slot not in TIME_SLOTS:
        raise ValueError(f"Invalid time slot: {time_slot}. Choose from {list(TIME_SLOTS.keys())}")

    sport_config = SPORTS_CONFIG[sport]

    # Use custom times if provided, otherwise use predefined time_slot
    if custom_start_time and custom_end_time:
        slot_config = {
            "start": custom_start_time,
            "end": custom_end_time
        }
    else:
        slot_config = TIME_SLOTS[time_slot]

    # Use center info from sport config if available, otherwise use defaults
    center_id = sport_config.get("center_id", CENTER_ID)
    center_name = sport_config.get("center_name", CENTER_NAME)

    return {
        "username": USERNAME,
        "password": PASSWORD,
        "user_id": USER_ID,
        "sport": sport,
        "activity_id": sport_config["activity_id"],
        "facility_id": sport_config["facility_id"],
        "facility_name": sport_config["facility_name"],
        "center_id": center_id,
        "center_name": center_name,
        "dataset_id": DATASET_ID,
        "date": booking_date,
        "start_time": slot_config["start"],
        "end_time": slot_config["end"],
    }
