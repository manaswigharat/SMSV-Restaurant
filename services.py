"""
Service layer for SMSV Restaurant.
Implements the core algorithms:
  • Greedy Table Allocation
  • Backtracking Cancellation & Replacement
  • Priority Queue Management
"""
from models import (
    get_waiting_bookings, get_available_tables, assign_table,
    cancel_booking, update_booking_status, get_all_bookings, get_booking_by_id
)


# ═══════════════════════════════════════════════════════════════
#  GREEDY TABLE ALLOCATION  (AOA Concept – Greedy Algorithm)
# ═══════════════════════════════════════════════════════════════
def greedy_allocate_tables():
    """
    Allocate tables to waiting bookings using a Greedy Algorithm.

    Strategy:
      1. Sort waiting bookings by priority (VIP first).
      2. For each booking, pick the *smallest* available table
         whose capacity >= group size.
      3. This minimises waste (greedy choice property).

    Returns a list of (booking, assigned_table) pairs.
    """
    waiting = get_waiting_bookings()          # already sorted by priority
    available = get_available_tables()        # sorted by capacity ASC
    allocated = []
    used_table_ids = set()

    for booking in waiting:
        people = booking['people_count']
        best_table = None

        for table in available:
            if table['id'] in used_table_ids:
                continue
            if table['capacity'] >= people:
                best_table = table
                break                          # greedy: first fit = smallest fit

        if best_table:
            assign_table(best_table['id'], booking['id'])
            used_table_ids.add(best_table['id'])
            allocated.append({
                'booking_id': booking['id'],
                'customer_name': booking['customer_name'],
                'people_count': people,
                'table_number': best_table['table_number'],
                'table_capacity': best_table['capacity']
            })

    return allocated


# ═══════════════════════════════════════════════════════════════
#  BACKTRACKING CANCELLATION  (AOA Concept – Backtracking)
# ═══════════════════════════════════════════════════════════════
def backtrack_find_replacement(freed_table_capacity, cancelled_date, cancelled_time,
                               waiting_bookings, index=0):
    """
    Recursive backtracking to find the best replacement booking.

    Constraints checked at each node:
      • people_count ≤ freed table capacity
      • booking_date matches the cancelled date
      • booking_time ≈ same time slot (within the same slot window)

    If the current candidate fails a constraint, we *backtrack* and
    try the next candidate in the queue.

    Returns the first valid booking dict, or None.
    """
    if index >= len(waiting_bookings):
        return None                             # base case – exhausted

    candidate = waiting_bookings[index]

    # ── constraint check ──
    fits_table = candidate['people_count'] <= freed_table_capacity
    same_date  = candidate['booking_date'] == cancelled_date
    compatible_time = _time_compatible(candidate['booking_time'], cancelled_time)

    if fits_table and same_date and compatible_time:
        return candidate                        # found valid replacement

    # ── backtrack ──
    return backtrack_find_replacement(
        freed_table_capacity, cancelled_date, cancelled_time,
        waiting_bookings, index + 1
    )


def _time_compatible(time_a, time_b):
    """Check if two time strings are within 2 hours of each other."""
    try:
        ha, ma = map(int, time_a.split(':'))
        hb, mb = map(int, time_b.split(':'))
        diff = abs((ha * 60 + ma) - (hb * 60 + mb))
        return diff <= 120
    except (ValueError, AttributeError):
        return True                             # if parsing fails, be permissive


def cancel_and_replace(booking_id):
    """
    Cancel a booking, then use backtracking to find a replacement.

    Steps:
      1. Cancel the booking and free its table.
      2. Gather the freed table's capacity and the cancelled slot.
      3. Run backtracking over the waiting queue.
      4. If a replacement is found, assign the freed table and notify.

    Returns (cancelled_booking_dict, replacement_info_dict | None).
    """
    booking = get_booking_by_id(booking_id)
    if not booking:
        return None, None

    table_id       = booking['table_id']
    table_capacity = booking['table_capacity'] if booking['table_capacity'] else 0
    cancel_date    = booking['booking_date']
    cancel_time    = booking['booking_time']

    # Step 1 – cancel
    cancelled = cancel_booking(booking_id)

    replacement_info = None

    if table_id and table_capacity > 0:
        # Step 2 – gather waiting queue
        waiting = get_waiting_bookings()

        # Step 3 – backtracking search
        replacement = backtrack_find_replacement(
            table_capacity, cancel_date, cancel_time, waiting
        )

        if replacement:
            # Step 4 – assign freed table to replacement
            assign_table(table_id, replacement['id'])
            notification = (
                f"🎉 Your booking has been upgraded due to a cancellation! "
                f"Table #{booking['table_number']} is now yours."
            )
            update_booking_status(
                replacement['id'], 'Upgraded', table_id, notification
            )
            replacement_info = {
                'booking_id': replacement['id'],
                'customer_name': replacement['customer_name'],
                'people_count': replacement['people_count'],
                'table_number': booking['table_number'],
                'notification': notification
            }

    return dict(booking) if booking else None, replacement_info


# ═══════════════════════════════════════════════════════════════
#  PRIORITY QUEUE HELPERS
# ═══════════════════════════════════════════════════════════════
def get_priority_queue():
    """Return the full booking list in priority-queue order."""
    return get_all_bookings()
