"""
Events configuration package for PolyU sports facility bookings.

This package provides static facility configurations and a function to generate
booking form data dynamically with user-provided parameters.

Usage:
    from events_config import FACILITIES, get_form_data

    # Get facility info
    facility = FACILITIES["table_tennis"]

    # Generate form data with dynamic parameters
    form_data = get_form_data(
        facility_key="table_tennis",
        user_id="442240",
        date="25 Oct 2025",
        start_time="08:30",
        end_time="09:30",
        csrf_token="your-csrf-token"
    )
"""

from .config import FACILITIES, get_form_data, DATASET_ID

# Export main components
__all__ = [
    'FACILITIES',
    'get_form_data',
    'DATASET_ID',
]
