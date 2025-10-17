"""
Example booking configurations
Quick examples for different scenarios
"""
from book import GenericBooking

# =============================================================================
# EXAMPLE 1: Book volleyball court at 8:30 AM
# =============================================================================
def book_volleyball_morning():
    booking = GenericBooking()
    booking.run(
        sport="volleyball",
        time_slot="morning_early",     # 08:30-09:30
        booking_date="25 Oct 2025",
        target_time_str="08:30:00",    # Submit at exactly 8:30:00 HKT
        network_offset_ms=200          # Send 200ms early
    )


# =============================================================================
# EXAMPLE 2: Book table tennis at 9:30 AM
# =============================================================================
def book_table_tennis_morning():
    booking = GenericBooking()
    booking.run(
        sport="table_tennis",
        time_slot="morning_mid",       # 09:30-10:30
        booking_date="25 Oct 2025",
        target_time_str="08:30:00",    # Submit at 8:30 AM
        network_offset_ms=200
    )


# =============================================================================
# EXAMPLE 3: Book volleyball at noon
# =============================================================================
def book_volleyball_noon():
    booking = GenericBooking()
    booking.run(
        sport="volleyball",
        time_slot="noon",              # 11:30-12:30
        booking_date="25 Oct 2025",
        target_time_str="08:30:00",
        network_offset_ms=200
    )


# =============================================================================
# EXAMPLE 4: Test booking (submit in 10 seconds)
# =============================================================================
def test_booking_soon():
    """Test the system with a booking in 10 seconds from now"""
    from datetime import datetime, timedelta
    import pytz

    hkt = pytz.timezone('Asia/Hong_Kong')
    target = datetime.now(hkt) + timedelta(seconds=10)
    target_time = target.strftime("%H:%M:%S")

    print(f"Testing with target time: {target_time}")

    booking = GenericBooking()
    booking.run(
        sport="table_tennis",
        time_slot="morning_mid",
        booking_date="18 Oct 2025",
        target_time_str=target_time,
        network_offset_ms=200
    )


# =============================================================================
# Run the example you want
# =============================================================================
if __name__ == "__main__":
    # Uncomment the one you want to run:

    # book_volleyball_morning()
    # book_table_tennis_morning()
    # book_volleyball_noon()
    test_booking_soon()
