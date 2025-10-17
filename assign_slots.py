"""
Simple slot assignment script
Reads accounts from CSV and assigns 1-hour slots based on date and time range
"""

import csv
from datetime import datetime, timedelta


def get_account_slots(csv_file, date, start_time, end_time):
    """
    Read accounts from CSV and assign 1-hour slots starting from xx:30 to xx:30
    
    Args:
        csv_file: Path to CSV file with accounts (name, user_id, password)
        date: Date string (e.g., "25 Oct 2025")
        start_time: Start time string (e.g., "08:30")
        end_time: End time string (e.g., "12:30")
    
    Returns:
        List of dicts with account info merged with their assigned slot
    """
    # Read accounts from CSV
    accounts = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({
                'username': row['username'],
                'name': row['name'],
                'user_id': row['user_id'],
                'password': row['password']
            })
    
    # Generate 1-hour slots
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")
    
    slots = []
    current = start_dt
    while current < end_dt:
        slot_end = current + timedelta(hours=1)
        slots.append({
            'start_time': current.strftime("%H:%M"),
            'end_time': slot_end.strftime("%H:%M")
        })
        current = slot_end
    
    # Merge accounts with slots
    account_slots = []
    for i, account in enumerate(accounts):
        if i < len(slots):
            account_slots.append({
                'username': account['username'],
                'name': account['name'],
                'user_id': account['user_id'],
                'password': account['password'],
                'date': date,
                'start_time': slots[i]['start_time'],
                'end_time': slots[i]['end_time']
            })
    
    return account_slots


# Example usage
if __name__ == "__main__":
    # Get merged account slots
    account_slots = get_account_slots(
        csv_file="accounts.csv",
        date="25 Oct 2025",
        start_time="08:30",
        end_time="12:30"
    )
    
    # Print results
    print("\nAccount Slot Assignments:")
    print("=" * 70)
    for slot in account_slots:
        print(f"{slot['name']:<12} | {slot['user_id']:<12} | {slot['start_time']}-{slot['end_time']} | {slot['date']}")
    print("=" * 70)
    
    # Now you can loop through and kickstart your booking script
    print("\nYou can now use this in your booking script:")
    print("for account_slot in account_slots:")
    print("    # Use account_slot['name'], account_slot['user_id'], etc.")
    print("    # kickstart_booking(account_slot)")

