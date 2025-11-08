"""
Master booking script - runs multiple accounts in parallel
Each account gets its own Selenium instance and fires requests simultaneously
"""

import multiprocessing
from book import GenericBooking
from assign_slots import get_account_slots
from datetime import datetime
import pytz
import os
from logger import setup_logging, restore_logging


def run_booking_for_account(account_slot, sport, target_time_str, network_offset_ms, headless, output_dir, pre_trigger_minutes, log_dir, num_requests, offset_ms_interval):
    """
    Run booking for a single account (executed in separate process)

    Args:
        account_slot: Dict with account info and time slot assignment
        sport: Sport type (e.g., "volleyball", "table_tennis")
        target_time_str: Target submission time (e.g., "08:30:00")
        network_offset_ms: Network offset in milliseconds
        headless: Run browser in headless mode
        output_dir: Directory to save output files
        pre_trigger_minutes: Minutes before target time to start browser and get token
        log_dir: Directory to save log files
        num_requests: Number of parallel requests to spam when target time is reached
        offset_ms_interval: Interval in milliseconds between each request (0 for simultaneous)
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
        # Create booking instance with unique account_id and log directory
        booking = GenericBooking(
            account_slot['user_id'],
            output_dir=output_dir,
            log_dir=log_dir
        )

        # Run booking with account-specific credentials and time slot
        booking.run(
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
            custom_end_time=account_slot['end_time'],
            # Pass pre-trigger time
            pre_trigger_minutes=pre_trigger_minutes,
            # Pass number of requests to spam
            num_requests=num_requests,
            # Pass offset interval between requests
            offset_ms_interval=offset_ms_interval
        )

        print(f"\n✅ [{account_username}] Booking process completed!")

    except (RuntimeError, ValueError, ConnectionError) as e:
        print(f"\n❌ [{account_username}] Error: {e}")


def run_parallel_bookings(
    csv_file="accounts.csv",
    booking_date="25 Oct 2025",
    slot_start_time="08:30",
    slot_end_time="12:30",
    sport="volleyball",
    target_time_str="08:30:00",
    network_offset_ms=200,
    headless=False,
    pre_trigger_minutes=15,
    log_dir="logs",
    num_requests=5,
    offset_ms_interval=0
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
        pre_trigger_minutes: Minutes before target time to start browser and get token (default 15)
        log_dir: Directory to save log files (default "logs")
        num_requests: Number of parallel requests to spam per account (default 5)
        offset_ms_interval: Interval in milliseconds between each request (default 0, simultaneous)
    """
    # Setup logging for master process
    master_logger = setup_logging(log_dir=log_dir, user_id="master")

    print("\n" + "="*70)
    print("🎯 MASTER BOOKING SCRIPT - PARALLEL EXECUTION")
    print("="*70)

    # Create timestamped output directory
    hkt = pytz.timezone('Asia/Hong_Kong')
    timestamp = datetime.now(hkt).strftime('%Y%m%d_%H%M%S')
    output_dir = f'booking_run_{timestamp}'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📁 Created output directory: {output_dir}")
    print(f"📁 Log directory: {log_dir}")
    print(f"📝 Master log file: {master_logger.log_path}")

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
    print("⚡ Configuration:")
    print(f"   Sport: {sport}")
    print(f"   Booking date: {booking_date}")
    print(f"   Target submission time: {target_time_str}")
    print(f"   Network offset: {network_offset_ms}ms")
    print(f"   Headless mode: {headless}")
    print(f"   Pre-trigger time: {pre_trigger_minutes} minutes before target")
    print(f"   Requests per account: {num_requests} (spam)")
    print(f"   Request interval: {offset_ms_interval}ms (0=simultaneous)")
    print(f"   Accounts to run: {len(account_slots)}")
    print("="*70 + "\n")

    # Confirm before starting
    hkt = pytz.timezone('Asia/Hong_Kong')
    now_hkt = datetime.now(hkt)
    print(f"⏰ Current HKT time: {now_hkt.strftime('%H:%M:%S')}")
    print(
        f"\n⚠️  WARNING: This will launch {len(account_slots)} browser instances in parallel!")
    print("   Make sure your system has enough resources.\n")

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
                headless,
                output_dir,
                pre_trigger_minutes,
                log_dir,
                num_requests,
                offset_ms_interval
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
    print(f"📁 All output files saved to: {output_dir}")
    print(f"📝 All log files saved to: {log_dir}")
    print("="*70)

    # Close master logger
    restore_logging(master_logger)


SPORT = "volleyball_shaw"  # Options: volleyball_shaw, volleyball_practice_hall, volleyball_fsch, table_tennis
TARGET_TIME = '08:30:00'  # Target submission time (HH:MM:SS)
START_TIME = "08:30"  # Start time of the time slot (HH:MM)
END_TIME = "12:30"  # End time of the time slot (HH:MM)
DATE = "01 Nov 2025"  # Booking date (YYYY-MM-DD)
PRE_TRIGGER_MINUTES = 15  # Start browser and get token X minutes before target time
NUM_REQUESTS = 7  # Number of requests to spam when target time is reached
NETWORK_OFFSET_MS = 15  # Network offset in milliseconds
OFFSET_MS_INTERVAL = 5  # Interval in milliseconds between requests

if __name__ == "__main__":
    # Example usage - customize these parameters
    run_parallel_bookings(
        csv_file="accounts.csv",
        booking_date=DATE,
        slot_start_time=START_TIME,
        slot_end_time=END_TIME,
        sport=SPORT,
        target_time_str=TARGET_TIME,
        network_offset_ms=NETWORK_OFFSET_MS,
        headless=False,  # Set to True to hide browser windows
        pre_trigger_minutes=PRE_TRIGGER_MINUTES,  # Start browser X minutes before target
        num_requests=NUM_REQUESTS,  # Number of parallel requests to spam per account
        offset_ms_interval=OFFSET_MS_INTERVAL  # Interval between requests (0=simultaneous)
    )
