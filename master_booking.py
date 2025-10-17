"""
Master booking script - runs multiple accounts in parallel
Each account gets its own Selenium instance and fires requests simultaneously
"""

import multiprocessing
from book import GenericBooking
from assign_slots import get_account_slots
from datetime import datetime
import pytz


def run_booking_for_account(account_slot, sport, target_time_str, network_offset_ms, headless):
    """
    Run booking for a single account (executed in separate process)

    Args:
        account_slot: Dict with account info and time slot assignment
        sport: Sport type (e.g., "volleyball", "table_tennis")
        target_time_str: Target submission time (e.g., "08:30:00")
        network_offset_ms: Network offset in milliseconds
        headless: Run browser in headless mode
    """
    account_username = account_slot['username']

    print(f"\n{'='*70}")
    print(f"🚀 [{account_username}] Starting booking process...")
    print(f"   Name: {account_slot['name']}")
    print(
        f"   Time slot: {account_slot['start_time']} - {account_slot['end_time']}")
    print(f"   Date: {account_slot['date']}")
    print(f"{'='*70}\n")

    try:
        # Create booking instance with unique account_id (using username for unique HTML files)
        booking = GenericBooking(account_slot['user_id'])

        # Run booking with account-specific credentials and time slot
        result = booking.run(
            sport=sport,
            time_slot=None,  # We'll use custom times from account_slot
            booking_date=account_slot['date'],
            target_time_str=target_time_str,
            network_offset_ms=network_offset_ms,
            headless=headless,
            # Pass custom credentials
            username=account_slot['username'],
            password=account_slot['password'],
            user_id=account_slot['user_id'],
            # Pass custom time slot
            custom_start_time=account_slot['start_time'],
            custom_end_time=account_slot['end_time']
        )

        print(f"\n✅ [{account_username}] Booking process completed!")
        return result

    except Exception as e:
        print(f"\n❌ [{account_username}] Error: {e}")
        return False


def run_parallel_bookings(
    csv_file="accounts.csv",
    booking_date="25 Oct 2025",
    slot_start_time="08:30",
    slot_end_time="12:30",
    sport="volleyball",
    target_time_str="08:30:00",
    network_offset_ms=200,
    headless=False
):
    """
    Master function to run parallel bookings for all accounts

    Args:
        csv_file: Path to CSV file with account information
        booking_date: Date to book (e.g., "25 Oct 2025")
        slot_start_time: Start of time range for slot assignment (e.g., "08:30")
        slot_end_time: End of time range for slot assignment (e.g., "12:30")
        sport: Sport to book (e.g., "volleyball", "table_tennis")
        target_time_str: Exact time to submit all bookings (e.g., "08:30:00")
        network_offset_ms: Network offset in milliseconds (default 200ms)
        headless: Run browsers in headless mode (default False)
    """
    print("\n" + "="*70)
    print("🎯 MASTER BOOKING SCRIPT - PARALLEL EXECUTION")
    print("="*70)

    # Get account slot assignments
    print(f"\n📋 Loading accounts from {csv_file}...")
    account_slots = get_account_slots(
        csv_file=csv_file,
        date=booking_date,
        start_time=slot_start_time,
        end_time=slot_end_time
    )

    print(f"✅ Loaded {len(account_slots)} accounts with slot assignments:\n")
    for slot in account_slots:
        print(
            f"   {slot['name']:<12} | {slot['username']:<12} | {slot['start_time']}-{slot['end_time']}")

    print("\n" + "="*70)
    print(f"⚡ Configuration:")
    print(f"   Sport: {sport}")
    print(f"   Booking date: {booking_date}")
    print(f"   Target submission time: {target_time_str}")
    print(f"   Network offset: {network_offset_ms}ms")
    print(f"   Headless mode: {headless}")
    print(f"   Accounts to run: {len(account_slots)}")
    print("="*70 + "\n")

    # Confirm before starting
    hkt = pytz.timezone('Asia/Hong_Kong')
    now_hkt = datetime.now(hkt)
    print(f"⏰ Current HKT time: {now_hkt.strftime('%H:%M:%S')}")
    print(
        f"\n⚠️  WARNING: This will launch {len(account_slots)} browser instances in parallel!")
    print("   Make sure your system has enough resources.\n")

    response = input("🚀 Ready to start? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Aborted by user")
        return

    print("\n" + "="*70)
    print("🔥 LAUNCHING PARALLEL BOOKINGS...")
    print("="*70 + "\n")

    # Create process pool and run bookings in parallel
    processes = []

    for account_slot in account_slots:
        # Create a separate process for each account
        process = multiprocessing.Process(
            target=run_booking_for_account,
            args=(
                account_slot,
                sport,
                target_time_str,
                network_offset_ms,
                headless
            )
        )
        processes.append(process)
        process.start()
        print(
            f"✅ Launched process for {account_slot['name']} ({account_slot['username']})")

    print(f"\n🔥 All {len(processes)} processes launched!")
    print("⏳ Waiting for all bookings to complete...\n")

    # Wait for all processes to complete
    for i, process in enumerate(processes):
        process.join()
        print(f"✅ Process {i+1}/{len(processes)} completed")

    print("\n" + "="*70)
    print("🎉 ALL BOOKINGS COMPLETED!")
    print("="*70)


SPORT = "table_tennis" # "volleyball" or "table_tennis"
TARGET_TIME = '04:49:00'
START_TIME = "12:30"
END_TIME = "16:30"
DATE = "23 Oct 2025"


if __name__ == "__main__":
    # Example usage - customize these parameters
    run_parallel_bookings(
        csv_file="accounts.csv",
        booking_date=DATE,
        slot_start_time=START_TIME,
        slot_end_time=END_TIME,
        sport=SPORT,
        target_time_str=TARGET_TIME,
        network_offset_ms=200,
        headless=False  # Set to True to hide browser windows
    )
    # run_parallel_bookings(
    #     csv_file="accounts.csv",
    #     booking_date="25 Oct 2025",
    #     slot_start_time="08:30",
    #     slot_end_time="12:30",
    #     sport="volleyball",
    #     target_time_str="08:30:00",
    #     network_offset_ms=200,
    #     headless=False  # Set to True to hide browser windows
    # )
