"""
SMSV Restaurant – Smart Priority Based Booking System
Main Flask Application

Demonstrates:
  • Priority Scheduling  (OS Concept)
  • Greedy Algorithm      (AOA – Table Allocation)
  • Backtracking          (AOA – Cancellation Replacement)
  • Queue Management
"""
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from database import init_db
from models import (
    create_booking, get_all_bookings, get_booking_by_id,
    get_waiting_bookings, get_all_tables, get_available_tables,
    cancel_booking, delete_booking, verify_admin,
    get_dashboard_stats, add_table, delete_table,
    update_booking_status, PRIORITY_MAP, TIME_LIMIT_MAP
)
from services import greedy_allocate_tables, cancel_and_replace, get_priority_queue

import os

app = Flask(__name__)
app.secret_key = 'smsv_restaurant_secret_key_2026'

# Initialize database on startup (needed for Render/gunicorn)
init_db()


# ═══════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ═══════════════════════════════════════════════════════

@app.route('/')
def home():
    """Landing page."""
    return render_template('index.html')


@app.route('/book', methods=['GET', 'POST'])
def book_table():
    """Booking form and submission."""
    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        people = int(request.form.get('people_count', 1))
        booking_type = request.form.get('booking_type', 'On-Spot')
        date = request.form.get('booking_date', '')
        time = request.form.get('booking_time', '')

        if not name or not date or not time:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('book_table'))

        booking_id = create_booking(name, people, booking_type, date, time)
        flash('Booking created successfully! Your booking is in the queue.', 'success')
        return redirect(url_for('booking_confirmation', booking_id=booking_id))

    return render_template('book.html')


@app.route('/confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    """Show booking confirmation details."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('home'))
    return render_template('confirmation.html', booking=booking)


@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking_route(booking_id):
    """Cancel a booking (customer-initiated) with backtracking replacement."""
    cancelled, replacement = cancel_and_replace(booking_id)
    if cancelled:
        flash('Your booking has been cancelled.', 'info')
        if replacement:
            flash(
                f"Table reassigned to {replacement['customer_name']} via backtracking!",
                'success'
            )
    else:
        flash('Booking not found.', 'error')
    # Redirect back to referrer or home
    ref = request.referrer
    if ref and 'dashboard' in ref:
        return redirect(url_for('admin_dashboard'))
    if ref and 'cancel' in ref:
        return redirect(url_for('cancellation_management'))
    return redirect(url_for('home'))


# ═══════════════════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if verify_admin(username, password):
            session['admin'] = True
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with statistics."""
    if not session.get('admin'):
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_login'))
    stats = get_dashboard_stats()
    bookings = get_all_bookings()
    tables = get_all_tables()
    return render_template('dashboard.html', stats=stats, bookings=bookings, tables=tables)


@app.route('/admin/queue')
def booking_queue():
    """Booking queue page sorted by priority."""
    if not session.get('admin'):
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_login'))
    bookings = get_priority_queue()
    return render_template('queue.html', bookings=bookings)


@app.route('/admin/allocate', methods=['GET', 'POST'])
def table_allocation():
    """Table allocation page using greedy algorithm."""
    if not session.get('admin'):
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_login'))

    allocated = []
    if request.method == 'POST':
        allocated = greedy_allocate_tables()
        if allocated:
            flash(f'Successfully allocated {len(allocated)} table(s) using Greedy Algorithm!', 'success')
        else:
            flash('No pending bookings to allocate or no tables available.', 'info')

    tables = get_all_tables()
    waiting = get_waiting_bookings()
    return render_template('allocation.html', tables=tables, waiting=waiting, allocated=allocated)


@app.route('/admin/cancellation')
def cancellation_management():
    """Cancellation management page."""
    if not session.get('admin'):
        flash('Please log in first.', 'error')
        return redirect(url_for('admin_login'))
    bookings = get_all_bookings()
    return render_template('cancellation.html', bookings=bookings)


@app.route('/admin/add_table', methods=['POST'])
def add_table_route():
    """Add a new table."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    table_number = int(request.form.get('table_number', 0))
    capacity = int(request.form.get('capacity', 2))
    if add_table(table_number, capacity):
        flash(f'Table #{table_number} ({capacity} seats) added!', 'success')
    else:
        flash('Failed to add table. Number may already exist.', 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_table/<int:table_id>', methods=['POST'])
def delete_table_route(table_id):
    """Delete a table."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    if delete_table(table_id):
        flash('Table deleted.', 'success')
    else:
        flash('Cannot delete an occupied table.', 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking_route(booking_id):
    """Permanently delete a booking."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    delete_booking(booking_id)
    flash('Booking deleted.', 'success')
    ref = request.referrer or url_for('admin_dashboard')
    return redirect(ref)


# ═══════════════════════════════════════════════════════
#  API ENDPOINTS (for AJAX)
# ═══════════════════════════════════════════════════════

@app.route('/api/booking/<int:booking_id>')
def api_booking(booking_id):
    """Get booking details as JSON."""
    booking = get_booking_by_id(booking_id)
    if booking:
        return jsonify(dict(booking))
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/stats')
def api_stats():
    """Get dashboard stats as JSON."""
    return jsonify(get_dashboard_stats())


# ═══════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "=" * 55)
    print("   SMSV Restaurant – Smart Booking System")
    print(f"   Running at http://127.0.0.1:{port}")
    print("=" * 55 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)
