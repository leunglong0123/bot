"""
Simple slot assignment script
Reads accounts from CSV and assigns 1-hour slots based on date and time range
"""

import csv
from datetime import datetime, timedelta


def get_account_slots(csv_file, date, start_time, end_time, allocation_strategy="priority"):
    """
    Read accounts from CSV and assign 1-hour slots starting from xx:30 to xx:30

    Args:
        csv_file: Path to CSV file with accounts (name, user_id, password)
        date: Date string (e.g., "25 Oct 2025")
        start_time: Start time string (e.g., "08:30")
        end_time: End time string (e.g., "12:30")
        allocation_strategy: How to assign accounts to slots
            - "sequential": 1 account per slot (old behavior)
            - "priority": Double up early slots (2,2,1,1 for 6 accounts/4 slots)
            - "balanced": Distribute evenly (2,2,2,0 or 1,2,2,1 depending on numbers)

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

    # Merge accounts with slots based on strategy
    account_slots = []

    if allocation_strategy == "sequential":
        # Old behavior: 1 account per slot
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

    elif allocation_strategy == "priority":
        # Priority strategy: Assign more accounts to earlier (more competitive) slots
        # For 6 accounts / 4 slots: [2, 2, 1, 1]
        # For 5 accounts / 4 slots: [2, 1, 1, 1]
        num_accounts = len(accounts)
        num_slots = len(slots)

        # Calculate how many accounts per slot
        base_accounts_per_slot = num_accounts // num_slots
        extra_accounts = num_accounts % num_slots

        # Assign extra accounts to early slots (higher priority)
        accounts_per_slot = []
        for i in range(num_slots):
            if i < extra_accounts:
                accounts_per_slot.append(base_accounts_per_slot + 1)
            else:
                accounts_per_slot.append(base_accounts_per_slot)

        # Assign accounts to slots
        account_index = 0
        for slot_index, slot in enumerate(slots):
            num_accounts_for_slot = accounts_per_slot[slot_index]
            for _ in range(num_accounts_for_slot):
                if account_index < num_accounts:
                    account_slots.append({
                        'username': accounts[account_index]['username'],
                        'name': accounts[account_index]['name'],
                        'user_id': accounts[account_index]['user_id'],
                        'password': accounts[account_index]['password'],
                        'date': date,
                        'start_time': slot['start_time'],
                        'end_time': slot['end_time']
                    })
                    account_index += 1

    elif allocation_strategy == "balanced":
        # Balanced strategy: Distribute evenly across all slots
        num_accounts = len(accounts)
        num_slots = len(slots)

        accounts_per_slot = num_accounts // num_slots
        extra_accounts = num_accounts % num_slots

        # Distribute evenly, with extras spread across middle slots
        account_index = 0
        for slot_index, slot in enumerate(slots):
            # Add extra to middle slots
            num_for_this_slot = accounts_per_slot
            if slot_index < extra_accounts:
                num_for_this_slot += 1

            for _ in range(num_for_this_slot):
                if account_index < num_accounts:
                    account_slots.append({
                        'username': accounts[account_index]['username'],
                        'name': accounts[account_index]['name'],
                        'user_id': accounts[account_index]['user_id'],
                        'password': accounts[account_index]['password'],
                        'date': date,
                        'start_time': slot['start_time'],
                        'end_time': slot['end_time']
                    })
                    account_index += 1

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

