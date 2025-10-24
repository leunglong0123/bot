"""
Static facility configurations for PolyU sports bookings.
Contains only facility-specific constants that don't change per booking.
"""

# Common constants
DATASET_ID = "18"

# Facility configurations - organized by sport and venue
FACILITIES = {
    "table_tennis": {
        "activity_id": "11",
        "facility_id": "16",
        "facility_name": "Table Tennis Table No. 1",
        "center_id": "1",
        "center_name": "Shaw Sports Complex",
        "dataset_id": DATASET_ID,
    },

    "volleyball_shaw": {
        "activity_id": "6",
        "facility_id": "1751",
        "facility_name": "Volleyball Court No. 3",
        "center_id": "1",
        "center_name": "Shaw Sports Complex",
        "dataset_id": DATASET_ID,
    },

    "volleyball_practice_hall": {
        "activity_id": "6",
        "facility_id": "8",
        "facility_name": "Volleyball Court No. 1",
        "center_id": "51",
        "center_name": "Shaw Sports Complex - Sports Practice Hall",
        "dataset_id": DATASET_ID,
    },

    "volleyball_fsch": {
        "activity_id": "6",
        "facility_id": "27",
        "facility_name": "Volleyball Court No. 2",
        "center_id": "2",
        "center_name": "Fong Shu Chuen Hall",
        "dataset_id": DATASET_ID,
    },
}


def get_form_data(facility_key, user_id, date, start_time, end_time, csrf_token=None):
    """
    Generate form data for booking submission.

    Args:
        facility_key: Key from FACILITIES dict (e.g., "table_tennis", "volleyball_shaw")
        user_id: User's PolyU ID
        date: Booking date string (e.g., "25 Oct 2025")
        start_time: Start time string (e.g., "08:30")
        end_time: End time string (e.g., "09:30")
        csrf_token: CSRF token (optional, can be set later)

    Returns:
        dict: Complete form data for booking submission

    Raises:
        ValueError: If facility_key is invalid
    """
    if facility_key not in FACILITIES:
        raise ValueError(
            f"Invalid facility key: {facility_key}. "
            f"Choose from {list(FACILITIES.keys())}"
        )

    facility = FACILITIES[facility_key]

    return {
        "dataSetId": facility["dataset_id"],
        "boBookingType.id": "1",
        "boBookingType.value": "INDV",
        "boBookingMode.value": "SPORT",
        "boBookingMode.id": "1",
        "userRefNum": "",
        "fbUserId": user_id,
        "grpFacilityIds": "",
        "repeatOccurrence": "false",
        "startDate": "",
        "startTime": "",
        "endDate": "",
        "endTime": "",
        "dayOfWeeks": "",
        "functionsAvailable": "false",
        "brcdNo": "",
        "phone": "",
        "onBehalfOfFbUserId": "",
        "byPassQuota": "false",
        "byPassChrgSchm": "false",
        "byPassBookingDaysLimit": "false",
        "searchFormString": (
            f"fbUserId={user_id}&bookType=INDV&"
            f"dataSetId={facility['dataset_id']}&"
            f"actvId={facility['activity_id']}&searchDate=&"
            f"ctrId={facility['center_id']}&facilityId="
        ),
        "extlPtyDclrId": "",
        "boMakeBookFacilities[0].ctrId": facility["center_id"],
        "boMakeBookFacilities[0].centerName": facility["center_name"],
        "boMakeBookFacilities[0].facilityId": facility["facility_id"],
        "boMakeBookFacilities[0].facilityName": facility["facility_name"],
        "boMakeBookFacilities[0].startDateTime": f"{date} {start_time}",
        "boMakeBookFacilities[0].endDateTime": f"{date} {end_time}",
        "declare": "on",
        "CSRFToken": csrf_token,
    }
