"""
Database initialization and connection management for SMSV Restaurant.
Uses SQLite for lightweight, file-based storage.
"""
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant.db')


def get_db():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database tables and seed default data."""
    conn = get_db()
    cursor = conn.cursor()

    # ── Bookings table ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            people_count INTEGER NOT NULL,
            booking_type TEXT NOT NULL CHECK(booking_type IN ('VIP', 'Pre-Booking', 'On-Spot')),
            priority INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            time_limit TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Waiting'
                CHECK(status IN ('Waiting', 'Confirmed', 'Cancelled', 'Completed', 'Upgraded')),
            table_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notification TEXT,
            FOREIGN KEY (table_id) REFERENCES tables(id)
        )
    ''')

    # ── Tables table ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL UNIQUE,
            capacity INTEGER NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1
        )
    ''')

    # ── Admin table ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Seed default tables if empty
    cursor.execute("SELECT COUNT(*) FROM tables")
    if cursor.fetchone()[0] == 0:
        default_tables = [
            (1, 2), (2, 2), (3, 2),
            (4, 4), (5, 4), (6, 4),
            (7, 6), (8, 6),
            (9, 8), (10, 8)
        ]
        cursor.executemany(
            "INSERT INTO tables (table_number, capacity) VALUES (?, ?)",
            default_tables
        )

    # Seed default admin if empty
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ('admin', 'admin123')
        )

    conn.commit()
    conn.close()
