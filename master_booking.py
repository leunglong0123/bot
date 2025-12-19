"""
Master booking script - runs multiple accounts in parallel
Each account gets its own Selenium instance and fires requests simultaneously

USAGE MODES:
1. BOOKING mode: Automated booking at target time with parallel requests
2. MANAGING mode: Opens My Record page for all accounts to view/cancel bookings

To switch modes, change USAGE_MODE variable:
- USAGE_MODE = "BOOKING"   - For automated booking
- USAGE_MODE = "MANAGING"  - For managing existing bookings
"""

import multiprocessing
from book import GenericBooking
from assign_slots import get_account_slots
from datetime import datetime
import pytz
import os
import time
import csv
from logger import setup_logging, restore_logging


def manage_account_record(account_info, headless, log_dir):
    """
    Login to account and navigate to My Record page for management

    Args:
        account_info: Dict with account credentials
        headless: Run browser in headless mode
        log_dir: Directory to save log files
    """
    account_username = account_info["username"]

    print(f"\n{'='*70}")
    print(f"🔍 [{account_username}] Opening My Record page...")
    print(f"   Name: {account_info['name']}")
    print(f"{'='*70}\n")

    try:
        # Create booking instance (we'll use it just for login)
        booking = GenericBooking(account_info["user_id"], log_dir=log_dir)

        # Start browser
        booking.start_browser(headless=headless)

        # Login
        if not booking.login(account_info["username"], account_info["password"]):
            print(f"❌ [{account_username}] Login failed")
            return False

        # Navigate to My Record page
        my_record_url = "https://www40.polyu.edu.hk/starspossfbstud/secure/ui_my_record/my_record.do"
        print(f"[{booking._get_hkt_time()}] 📄 Navigating to My Record page...")
        booking.page.goto(my_record_url, wait_until="networkidle", timeout=30000)

        print(
            f"[{booking._get_hkt_time()}] ✅ [{account_username}] My Record page loaded!"
        )
        print(f"[{booking._get_hkt_time()}] 🌐 Browser will stay open for management")
        print(
            f"[{booking._get_hkt_time()}] 💡 Press Ctrl+C when done to close all browsers\n"
        )

        # Keep browser open indefinitely
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print(
                f"\n[{booking._get_hkt_time()}] 🛑 Closing browser for {account_username}..."
            )
            booking.close_browser()

    except Exception as e:
        print(f"\n❌ [{account_username}] Error: {e}")


def run_booking_for_account(
    account_slot,
    sport,
    target_time_str,
    network_offset_ms,
    headless,
    output_dir,
    pre_trigger_minutes,
    log_dir,
    num_requests,
    offset_ms_interval,
):
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
    account_username = account_slot["username"]

    print(f"\n{'='*70}")
    print(f"🚀 [{account_username}] Starting booking process...")
    print(f"   Name: {account_slot['name']}")
    print(f"   Time slot: {account_slot['start_time']} - {account_slot['end_time']}")
    print(f"   Date: {account_slot['date']}")
    print(f"{'='*70}\n")

    try:
        # Create booking instance with unique account_id and log directory
        booking = GenericBooking(
            account_slot["user_id"], output_dir=output_dir, log_dir=log_dir
        )

        # Run booking with account-specific credentials and time slot
        booking.run(
            sport=sport,
            time_slot=None,  # We'll use custom times from account_slot
            booking_date=account_slot["date"],
            target_time_str=target_time_str,
            network_offset_ms=network_offset_ms,
            headless=headless,
            # Pass custom credentials
            username=account_slot["username"],
            password=account_slot["password"],
            user_id=account_slot["user_id"],
            # Pass custom time slot
            custom_start_time=account_slot["start_time"],
            custom_end_time=account_slot["end_time"],
            # Pass pre-trigger time
            pre_trigger_minutes=pre_trigger_minutes,
            # Pass number of requests to spam
            num_requests=num_requests,
            # Pass offset interval between requests
            offset_ms_interval=offset_ms_interval,
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
    offset_ms_interval=0,
    allocation_strategy="priority",
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
        allocation_strategy: How to assign accounts to slots (default "priority")
            - "sequential": 1 account per slot
            - "priority": More accounts on early (competitive) slots
            - "balanced": Evenly distribute accounts across slots
    """
    # Setup logging for master process
    master_logger = setup_logging(log_dir=log_dir, user_id="master")

    print("\n" + "=" * 70)
    print("🎯 MASTER BOOKING SCRIPT - PARALLEL EXECUTION")
    print("=" * 70)

    # Create timestamped output directory
    hkt = pytz.timezone("Asia/Hong_Kong")
    timestamp = datetime.now(hkt).strftime("%Y%m%d_%H%M%S")
    output_dir = f"booking_run_{timestamp}"
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
        end_time=slot_end_time,
        allocation_strategy=allocation_strategy,
    )

    print(f"✅ Loaded {len(account_slots)} accounts with slot assignments:\n")
    for slot in account_slots:
        print(
            f"   {slot['name']:<12} | {slot['username']:<12} | {slot['start_time']}-{slot['end_time']}"
        )

    print("\n" + "=" * 70)
    print("⚡ Configuration:")
    print(f"   Sport: {sport}")
    print(f"   Booking date: {booking_date}")
    print(f"   Target submission time: {target_time_str}")
    print(f"   Network offset: {network_offset_ms}ms")
    print(f"   Headless mode: {headless}")
    print(f"   Pre-trigger time: {pre_trigger_minutes} minutes before target")
    print(f"   Requests per account: {num_requests} (spam)")
    print(f"   Request interval: {offset_ms_interval}ms (0=simultaneous)")
    print(f"   Allocation strategy: {allocation_strategy}")
    print(f"   Accounts to run: {len(account_slots)}")
    print("=" * 70 + "\n")

    # Confirm before starting
    hkt = pytz.timezone("Asia/Hong_Kong")
    now_hkt = datetime.now(hkt)
    print(f"⏰ Current HKT time: {now_hkt.strftime('%H:%M:%S')}")
    print(
        f"\n⚠️  WARNING: This will launch {len(account_slots)} browser instances in parallel!"
    )
    print("   Make sure your system has enough resources.\n")

    print("\n" + "=" * 70)
    print("🔥 LAUNCHING PARALLEL BOOKINGS...")
    print("=" * 70 + "\n")

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
                offset_ms_interval,
            ),
        )
        processes.append(process)
        process.start()
        print(
            f"✅ Launched process for {account_slot['name']} ({account_slot['username']})"
        )

    print(f"\n🔥 All {len(processes)} processes launched!")
    print("⏳ Waiting for all bookings to complete...\n")

    # Wait for all processes to complete
    for i, process in enumerate(processes):
        process.join()
        print(f"✅ Process {i+1}/{len(processes)} completed")

    print("\n" + "=" * 70)
    print("🎉 ALL BOOKINGS COMPLETED!")
    print(f"📁 All output files saved to: {output_dir}")
    print(f"📝 All log files saved to: {log_dir}")
    print("=" * 70)

    # Close master logger
    restore_logging(master_logger)


def run_management_mode(csv_file="accounts.csv", headless=False, log_dir="logs"):
    """
    Open My Record page for all accounts to manage bookings

    Args:
        csv_file: Path to CSV file with account information
        headless: Run browsers in headless mode (default False)
        log_dir: Directory to save log files (default "logs")
    """
    # Setup logging for master process
    master_logger = setup_logging(log_dir=log_dir, user_id="master")

    print("\n" + "=" * 70)
    print("📋 MANAGEMENT MODE - MY RECORD PAGE")
    print("=" * 70)

    # Read accounts from CSV
    print(f"\n📋 Loading accounts from {csv_file}...")
    accounts = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(
                {
                    "username": row["username"],
                    "name": row["name"],
                    "user_id": row["user_id"],
                    "password": row["password"],
                }
            )

    print(f"✅ Loaded {len(accounts)} accounts:\n")
    for account in accounts:
        print(f"   {account['name']:<12} | {account['username']:<12}")

    print("\n" + "=" * 70)
    print("⚡ Configuration:")
    print(f"   Headless mode: {headless}")
    print(f"   Accounts to open: {len(accounts)}")
    print("=" * 70 + "\n")

    print(
        f"\n⚠️  WARNING: This will launch {len(accounts)} browser instances in parallel!"
    )
    print("   Make sure your system has enough resources.\n")

    print("\n" + "=" * 70)
    print("🔥 OPENING MY RECORD PAGES...")
    print("=" * 70 + "\n")

    # Create process pool and open browsers in parallel
    processes = []

    for account in accounts:
        # Create a separate process for each account
        process = multiprocessing.Process(
            target=manage_account_record, args=(account, headless, log_dir)
        )
        processes.append(process)
        process.start()
        print(f"✅ Launched browser for {account['name']} ({account['username']})")

    print(f"\n🔥 All {len(processes)} browsers launched!")
    print("⏳ All browsers are open and ready for management")
    print("💡 Press Ctrl+C to close all browsers and exit\n")

    # Wait for all processes to complete (they run until Ctrl+C)
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("🛑 SHUTTING DOWN ALL BROWSERS...")
        print("=" * 70)
        for i, process in enumerate(processes):
            process.terminate()
            process.join()
            print(f"✅ Closed browser {i+1}/{len(processes)}")

    print("\n" + "=" * 70)
    print("🎉 ALL BROWSERS CLOSED!")
    print("=" * 70)

    # Close master logger
    restore_logging(master_logger)


USAGE_MODE = "BOOKING"  # BOOKING/MANAGING
SPORT = "volleyball_shaw"  # Options: volleyball_shaw, volleyball_practice_hall, volleyball_fsch, table_tennis
TARGET_TIME = "08:30:00"  # Target submission time (HH:MM:SS)
START_TIME = "13:30"  # Start time of the time slot (HH:MM)
END_TIME = "19:30"  # End time of the time slot (HH:MM)
DATE = "27 Dec 2025"  # Booking date (YYYY-MM-DD)
PRE_TRIGGER_MINUTES = 10  # Start browser and get token X minutes before target time
NUM_REQUESTS = 8  # Number of requests to spam when target time is reached
NETWORK_OFFSET_MS = 50  # Network offset in milliseconds
OFFSET_MS_INTERVAL = 0  # Interval in milliseconds between requests (0=simultaneous)
ALLOCATION_STRATEGY = (
    "priority"  # "priority" (recommended), "balanced", or "sequential"
)

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    if USAGE_MODE == "BOOKING":
        # Booking mode - run parallel bookings at target time
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
            offset_ms_interval=OFFSET_MS_INTERVAL,  # Interval between requests (0=simultaneous)
            allocation_strategy=ALLOCATION_STRATEGY,  # How to distribute accounts across slots
        )
    elif USAGE_MODE == "MANAGING":
        # Management mode - open My Record page for all accounts
        run_management_mode(
            csv_file="accounts.csv",
            headless=False,  # Set to True to hide browser windows
            log_dir="logs",
        )
    else:
        print(f"❌ Invalid USAGE_MODE: {USAGE_MODE}")
        print("   Valid options: 'BOOKING' or 'MANAGING'")
        exit(1)
