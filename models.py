"""
Data models and database operations for SMSV Restaurant.
Provides CRUD operations for bookings, tables, and admin authentication.
"""
from database import get_db


# ═══════════════════════════════════════════════════════
#  PRIORITY MAPPING  (OS Concept – Priority Scheduling)
# ═══════════════════════════════════════════════════════
PRIORITY_MAP = {
    'VIP': 1,          # Highest priority
    'Pre-Booking': 2,  # Medium priority
    'On-Spot': 3       # Lowest priority
}

TIME_LIMIT_MAP = {
    'VIP': 'Unlimited',
    'Pre-Booking': '2 Hours',
    'On-Spot': '1 Hour'
}


# ═══════════════════════════════════════════════════════
#  BOOKING OPERATIONS
# ═══════════════════════════════════════════════════════

def create_booking(name, people_count, booking_type, date, time):
    """Create a new booking and return its ID."""
    db = get_db()
    priority = PRIORITY_MAP.get(booking_type, 3)
    time_limit = TIME_LIMIT_MAP.get(booking_type, '1 Hour')

    cursor = db.execute(
        '''INSERT INTO bookings
           (customer_name, people_count, booking_type, priority,
            booking_date, booking_time, time_limit, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'Waiting')''',
        (name, people_count, booking_type, priority, date, time, time_limit)
    )
    db.commit()
    booking_id = cursor.lastrowid
    db.close()
    return booking_id


def get_all_bookings():
    """Get all bookings ordered by priority (highest first), then date/time."""
    db = get_db()
    bookings = db.execute(
        '''SELECT b.*, t.table_number, t.capacity as table_capacity
           FROM bookings b
           LEFT JOIN tables t ON b.table_id = t.id
           ORDER BY b.priority ASC, b.booking_date ASC, b.booking_time ASC'''
    ).fetchall()
    db.close()
    return bookings


def get_booking_by_id(booking_id):
    """Get a single booking by ID."""
    db = get_db()
    booking = db.execute(
        '''SELECT b.*, t.table_number, t.capacity as table_capacity
           FROM bookings b
           LEFT JOIN tables t ON b.table_id = t.id
           WHERE b.id = ?''',
        (booking_id,)
    ).fetchone()
    db.close()
    return booking


def get_waiting_bookings():
    """Get all bookings in 'Waiting' status, sorted by priority."""
    db = get_db()
    bookings = db.execute(
        '''SELECT * FROM bookings
           WHERE status = 'Waiting'
           ORDER BY priority ASC, booking_date ASC, booking_time ASC'''
    ).fetchall()
    db.close()
    return bookings


def update_booking_status(booking_id, status, table_id=None, notification=None):
    """Update a booking's status, optionally assigning a table."""
    db = get_db()
    if table_id is not None:
        db.execute(
            '''UPDATE bookings SET status = ?, table_id = ?, notification = ?
               WHERE id = ?''',
            (status, table_id, notification, booking_id)
        )
    else:
        db.execute(
            '''UPDATE bookings SET status = ?, notification = ?
               WHERE id = ?''',
            (status, notification, booking_id)
        )
    db.commit()
    db.close()


def cancel_booking(booking_id):
    """Cancel a booking and free its table."""
    db = get_db()
    booking = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if booking and booking['table_id']:
        db.execute("UPDATE tables SET is_available = 1 WHERE id = ?", (booking['table_id'],))
    db.execute(
        "UPDATE bookings SET status = 'Cancelled', table_id = NULL WHERE id = ?",
        (booking_id,)
    )
    db.commit()
    db.close()
    return booking


def delete_booking(booking_id):
    """Permanently delete a booking and free its table."""
    db = get_db()
    booking = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if booking and booking['table_id']:
        db.execute("UPDATE tables SET is_available = 1 WHERE id = ?", (booking['table_id'],))
    db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    db.commit()
    db.close()


# ═══════════════════════════════════════════════════════
#  TABLE OPERATIONS
# ═══════════════════════════════════════════════════════

def get_all_tables():
    """Get all tables."""
    db = get_db()
    tables = db.execute(
        "SELECT * FROM tables ORDER BY capacity ASC, table_number ASC"
    ).fetchall()
    db.close()
    return tables


def get_available_tables():
    """Get only available (unoccupied) tables, sorted by capacity ascending."""
    db = get_db()
    tables = db.execute(
        "SELECT * FROM tables WHERE is_available = 1 ORDER BY capacity ASC"
    ).fetchall()
    db.close()
    return tables


def assign_table(table_id, booking_id):
    """Mark table as occupied and assign it to a booking."""
    db = get_db()
    db.execute("UPDATE tables SET is_available = 0 WHERE id = ?", (table_id,))
    db.execute(
        "UPDATE bookings SET table_id = ?, status = 'Confirmed' WHERE id = ?",
        (table_id, booking_id)
    )
    db.commit()
    db.close()


def free_table(table_id):
    """Mark a table as available again."""
    db = get_db()
    db.execute("UPDATE tables SET is_available = 1 WHERE id = ?", (table_id,))
    db.commit()
    db.close()


def add_table(table_number, capacity):
    """Add a new table to the restaurant."""
    db = get_db()
    try:
        db.execute(
            "INSERT INTO tables (table_number, capacity) VALUES (?, ?)",
            (table_number, capacity)
        )
        db.commit()
        db.close()
        return True
    except Exception:
        db.close()
        return False


def delete_table(table_id):
    """Delete a table (only if it's available)."""
    db = get_db()
    table = db.execute("SELECT * FROM tables WHERE id = ? AND is_available = 1", (table_id,)).fetchone()
    if table:
        db.execute("DELETE FROM tables WHERE id = ?", (table_id,))
        db.commit()
        db.close()
        return True
    db.close()
    return False


# ═══════════════════════════════════════════════════════
#  ADMIN OPERATIONS
# ═══════════════════════════════════════════════════════

def verify_admin(username, password):
    """Verify admin credentials."""
    db = get_db()
    admin = db.execute(
        "SELECT * FROM admin WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    db.close()
    return admin is not None


# ═══════════════════════════════════════════════════════
#  STATISTICS
# ═══════════════════════════════════════════════════════

def get_dashboard_stats():
    """Compute summary statistics for the admin dashboard."""
    db = get_db()

    total = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    vip = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE booking_type = 'VIP'"
    ).fetchone()[0]
    confirmed = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'"
    ).fetchone()[0]
    waiting = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Waiting'"
    ).fetchone()[0]
    cancelled = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Cancelled'"
    ).fetchone()[0]

    total_tables = db.execute("SELECT COUNT(*) FROM tables").fetchone()[0]
    occupied = db.execute(
        "SELECT COUNT(*) FROM tables WHERE is_available = 0"
    ).fetchone()[0]

    # Revenue estimate: VIP ₹2000, Pre-Booking ₹1500, On-Spot ₹1000
    rev_vip = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE booking_type='VIP' AND status IN ('Confirmed','Completed')"
    ).fetchone()[0] * 2000
    rev_pre = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE booking_type='Pre-Booking' AND status IN ('Confirmed','Completed')"
    ).fetchone()[0] * 1500
    rev_spot = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE booking_type='On-Spot' AND status IN ('Confirmed','Completed')"
    ).fetchone()[0] * 1000
    revenue = rev_vip + rev_pre + rev_spot

    db.close()
    return {
        'total_bookings': total,
        'vip_bookings': vip,
        'confirmed_bookings': confirmed,
        'waiting_bookings': waiting,
        'cancelled_bookings': cancelled,
        'total_tables': total_tables,
        'occupied_tables': occupied,
        'available_tables': total_tables - occupied,
        'utilization': round((occupied / total_tables * 100), 1) if total_tables else 0,
        'total_revenue': revenue
    }
