from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from datetime import datetime, timedelta
import mysql.connector
import os
from decimal import Decimal
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key in production

# Home Page
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get available parking spots count
    cursor.execute("SELECT COUNT(*) as count FROM parking_spots WHERE status = 'available'")
    available_spots = cursor.fetchone()['count']
    
    # Get total parking spots count
    cursor.execute("SELECT COUNT(*) as count FROM parking_spots")
    total_spots = cursor.fetchone()['count']
    
    # Get today's bookings count
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE DATE(start_time) = %s", (today,))
    todays_bookings = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return render_template('home.html', 
                          available_spots=available_spots,
                          total_spots=total_spots,
                          todays_bookings=todays_bookings)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check user credentials based on role
        if role == 'user':
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = 'user'
                flash('Login successful!', 'success')
                return redirect(url_for('user_dashboard'))
        elif role == 'staff':
            cursor.execute("SELECT * FROM staff WHERE username = %s AND password = %s", (username, password))
            staff = cursor.fetchone()
            if staff:
                session['staff_id'] = staff['staff_id']
                session['username'] = staff['username']
                session['role'] = 'staff'
                flash('Login successful!', 'success')
                return redirect(url_for('staff_dashboard'))
        elif role == 'admin':
            cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
            admin = cursor.fetchone()
            if admin:
                session['admin_id'] = admin['admin_id']
                session['username'] = admin['username']
                session['role'] = 'admin'
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))

        flash('Invalid credentials. Please try again.', 'error')
    return render_template('auth/login.html')

# User Dashboard
@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please login to access your dashboard.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch available parking spots
    cursor.execute("SELECT * FROM parking_spots WHERE status = 'available'")
    parking_spots = cursor.fetchall()

    # Fetch user bookings
    cursor.execute("""
        SELECT b.*, p.location 
        FROM bookings b 
        JOIN parking_spots p ON b.spot_id = p.spot_id 
        WHERE b.user_id = %s
    """, (session['user_id'],))
    bookings = cursor.fetchall()

    return render_template('user/dashboard.html', parking_spots=parking_spots, bookings=bookings)

# Staff Dashboard
@app.route('/staff/dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        flash('Please login as staff to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all bookings
    cursor.execute("""
        SELECT b.*, u.username, p.location 
        FROM bookings b 
        JOIN users u ON b.user_id = u.user_id 
        JOIN parking_spots p ON b.spot_id = p.spot_id
    """)
    bookings = cursor.fetchall()

    # Fetch all parking spots
    cursor.execute("SELECT * FROM parking_spots")
    parking_spots = cursor.fetchall()

    return render_template('staff/dashboard.html', bookings=bookings, parking_spots=parking_spots)

# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please login as admin to access this page.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all parking spots
    cursor.execute("SELECT * FROM parking_spots")
    parking_spots = cursor.fetchall()

    return render_template('admin/dashboard.html', parking_spots=parking_spots)

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert new user into the appropriate table based on role
            if role == 'user':
                cursor.execute(
                    "INSERT INTO users (username, password, email, phone) VALUES (%s, %s, %s, %s)",
                    (username, password, email, phone)
                )
            elif role == 'staff':
                cursor.execute(
                    "INSERT INTO staff (username, password, email, phone) VALUES (%s, %s, %s, %s)",
                    (username, password, email, phone)
                )
            elif role == 'admin':
                cursor.execute(
                    "INSERT INTO admins (username, password, email) VALUES (%s, %s, %s)",
                    (username, password, email)
                )

            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# Add Parking Spot (Admin)
@app.route('/admin/add_spot', methods=['POST'])
def add_spot():
    if 'admin_id' not in session:
        flash('Admin access required.', 'error')
        return redirect(url_for('login'))

    location = request.form['location']
    price_per_hour = request.form['price_per_hour']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new parking spot
    cursor.execute(
        "INSERT INTO parking_spots (location, price_per_hour) VALUES (%s, %s)",
        (location, price_per_hour)
    )
    conn.commit()

    flash('Parking spot added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Edit Parking Spot (Admin)
@app.route('/admin/edit_spot/<int:spot_id>', methods=['GET', 'POST'])
def edit_spot(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        location = request.form['location']
        status = request.form['status']
        price_per_hour = request.form['price_per_hour']

        # Update parking spot
        cursor.execute(
            "UPDATE parking_spots SET location = %s, status = %s, price_per_hour = %s WHERE spot_id = %s",
            (location, status, price_per_hour, spot_id)
        )
        conn.commit()

        flash('Parking spot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch parking spot details
    cursor.execute("SELECT * FROM parking_spots WHERE spot_id = %s", (spot_id,))
    spot = cursor.fetchone()

    return render_template('admin/edit_spot.html', spot=spot)

# Delete Parking Spot (Admin)
@app.route('/admin/delete_spot/<int:spot_id>')
def delete_spot(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete parking spot
    cursor.execute("DELETE FROM parking_spots WHERE spot_id = %s", (spot_id,))
    conn.commit()

    flash('Parking spot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# User Profile
@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        current_password = request.form['current_password']
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Verify current password
        cursor.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", 
                      (session['user_id'], current_password))
        user = cursor.fetchone()
        
        if user:
            # Update profile information
            if new_password and new_password == confirm_password:
                cursor.execute(
                    "UPDATE users SET username = %s, email = %s, phone = %s, password = %s WHERE user_id = %s",
                    (username, email, phone, new_password, session['user_id'])
                )
                flash('Profile updated with new password!', 'success')
            else:
                cursor.execute(
                    "UPDATE users SET username = %s, email = %s, phone = %s WHERE user_id = %s",
                    (username, email, phone, session['user_id'])
                )
                flash('Profile updated successfully!', 'success')
            
            conn.commit()
            session['username'] = username
            return redirect(url_for('user_dashboard'))
        else:
            flash('Current password is incorrect!', 'error')
    
    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    return render_template('user/profile.html', user=user)

# Book a Parking Spot
@app.route('/user/book_spot', methods=['POST'])
def book_spot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    spot_id = request.form['spot_id']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if spot is available
    cursor.execute("SELECT * FROM parking_spots WHERE spot_id = %s AND status = 'available'", (spot_id,))
    if not cursor.fetchone():
        flash('This parking spot is no longer available!', 'error')
        return redirect(url_for('user_dashboard'))
    
    try:
        # Create booking
        cursor.execute(
            "INSERT INTO bookings (user_id, spot_id, start_time, end_time) VALUES (%s, %s, %s, %s)",
            (session['user_id'], spot_id, start_time, end_time)
        )
        
        # Update spot status to occupied
        cursor.execute("UPDATE parking_spots SET status = 'occupied' WHERE spot_id = %s", (spot_id,))
        
        conn.commit()
        flash('Booking created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating booking: {str(e)}', 'error')
    
    return redirect(url_for('user_dashboard'))

# View Booking Details
@app.route('/user/booking/<int:booking_id>')
def view_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch booking details
    cursor.execute("""
        SELECT b.*, p.location, p.price_per_hour 
        FROM bookings b 
        JOIN parking_spots p ON b.spot_id = p.spot_id 
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, session['user_id']))
    
    booking = cursor.fetchone()
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Calculate duration and cost
    start_time = booking['start_time']
    end_time = booking['end_time']
    duration = (end_time - start_time).total_seconds() / 3600  # hours
    total_cost = float(booking['price_per_hour']) * duration
    
    return render_template('user/booking.html', booking=booking, duration=round(duration, 2), total_cost=round(total_cost, 2))

# Cancel Booking
@app.route('/user/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if booking exists and belongs to user
    cursor.execute("""
        SELECT b.*, p.spot_id 
        FROM bookings b 
        JOIN parking_spots p ON b.spot_id = p.spot_id 
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, session['user_id']))
    
    booking = cursor.fetchone()
    
    if not booking:
        flash('Booking not found!', 'error')
    elif booking['status'] != 'pending':
        flash('Only pending bookings can be cancelled!', 'error')
    else:
        # Update booking status
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s", (booking_id,))
        
        # Update parking spot status
        cursor.execute("UPDATE parking_spots SET status = 'available' WHERE spot_id = %s", (booking['spot_id'],))
        
        conn.commit()
        flash('Booking cancelled successfully!', 'success')
    
    return redirect(url_for('user_dashboard'))

# Make Payment
@app.route('/user/make_payment/<int:booking_id>', methods=['GET', 'POST'])
def make_payment(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if booking exists and belongs to user
    cursor.execute("""
        SELECT b.*, p.location, p.price_per_hour 
        FROM bookings b 
        JOIN parking_spots p ON b.spot_id = p.spot_id 
        WHERE b.booking_id = %s AND b.user_id = %s
    """, (booking_id, session['user_id']))
    
    booking = cursor.fetchone()
    
    if not booking:
        flash('Booking not found!', 'error')
        return redirect(url_for('user_dashboard'))
    
    if booking['payment_status'] == 'paid':
        flash('This booking has already been paid!', 'error')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        payment_number = request.form.get('payment_number', '')
        expiry_date = request.form.get('expiry_date', '')
        cvv = request.form.get('cvv', '')
        
        # Calculate payment amount
        start_time = booking['start_time']
        end_time = booking['end_time']
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        amount = float(booking['price_per_hour']) * duration
        
        # Create transaction record with payment details
        cursor.execute(
            "INSERT INTO transactions (booking_id, payment_method, amount, payment_number, expiry_date) VALUES (%s, %s, %s, %s, %s)",
            (booking_id, payment_method, amount, payment_number, expiry_date)
        )
        
        # Update booking payment status based on payment method
        if payment_method == 'cash':
            payment_status = 'paid'
            booking_status = 'confirmed'
        else:
            payment_status = 'pending'
            booking_status = 'pending_payment'
        
        cursor.execute(
            "UPDATE bookings SET payment_status = %s, status = %s WHERE booking_id = %s",
            (payment_status, booking_status, booking_id)
        )
        
        conn.commit()
        
        if payment_method == 'cash':
            flash('Payment successful!', 'success')
        else:
            flash('Payment submitted and pending verification. Staff will review your payment shortly.', 'info')
        
        return redirect(url_for('user_dashboard'))
    
    # Calculate amount for display
    start_time = booking['start_time']
    end_time = booking['end_time']
    duration = (end_time - start_time).total_seconds() / 3600  # hours
    total_cost = float(booking['price_per_hour']) * duration
    
    return render_template('user/booking.html', booking=booking, duration=round(duration, 2), total_cost=round(total_cost, 2))

# Staff - Verify Booking
@app.route('/staff/verify_booking', methods=['GET', 'POST'])
def verify_booking():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    
    booking = None
    
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch booking details
        cursor.execute("""
            SELECT b.*, u.username, p.location 
            FROM bookings b 
            JOIN users u ON b.user_id = u.user_id 
            JOIN parking_spots p ON b.spot_id = p.spot_id 
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            flash('Booking not found!', 'error')
    
    return render_template('staff/verify_booking.html', booking=booking)

# Staff - Confirm Booking
@app.route('/staff/confirm_booking/<int:booking_id>')
def confirm_booking(booking_id):
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update booking status
    cursor.execute("UPDATE bookings SET status = 'confirmed' WHERE booking_id = %s", (booking_id,))
    conn.commit()
    
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('staff_dashboard'))

# Staff - Cancel Booking
@app.route('/staff/cancel_booking/<int:booking_id>')
def cancel_booking_staff(booking_id):
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get booking and spot info
    cursor.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
    booking = cursor.fetchone()
    
    if booking:
        # Update booking status
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s", (booking_id,))
        
        # Update parking spot status
        cursor.execute("UPDATE parking_spots SET status = 'available' WHERE spot_id = %s", (booking['spot_id'],))
        
        conn.commit()
        flash('Booking cancelled successfully!', 'success')
    else:
        flash('Booking not found!', 'error')
    
    return redirect(url_for('staff_dashboard'))

# Staff - Handle Entry/Exit
@app.route('/staff/handle_entry_exit', methods=['GET', 'POST'])
def handle_entry_exit():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    
    booking = None
    message = None
    success = False
    
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        action_type = request.form['action_type']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch booking details
        cursor.execute("""
            SELECT b.*, u.username, p.location, p.spot_id 
            FROM bookings b 
            JOIN users u ON b.user_id = u.user_id 
            JOIN parking_spots p ON b.spot_id = p.spot_id 
            WHERE b.booking_id = %s
        """, (booking_id,))
        
        booking = cursor.fetchone()
        
        if not booking:
            message = 'Booking not found!'
        elif booking['status'] != 'confirmed':
            message = 'Only confirmed bookings can be processed for entry/exit!'
        elif booking['payment_status'] != 'paid':
            message = 'Payment must be completed before entry/exit!'
        else:
            # Handle entry/exit
            if action_type == 'entry':
                # Update parking spot status
                cursor.execute("UPDATE parking_spots SET status = 'occupied' WHERE spot_id = %s", (booking['spot_id'],))
                message = f"Vehicle entry processed for booking #{booking_id}."
                success = True
            else:  # exit
                # Update parking spot status
                cursor.execute("UPDATE parking_spots SET status = 'available' WHERE spot_id = %s", (booking['spot_id'],))
                message = f"Vehicle exit processed for booking #{booking_id}."
                success = True
            
            conn.commit()
    
    return render_template('staff/handle_entry_exit.html', booking=booking, message=message, success=success)

# Admin - Generate Reports
@app.route('/admin/generate_report', methods=['GET', 'POST'])
def generate_report():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    report_data = None
    report_title = None
    start_date = None
    end_date = None
    report_type = None
    total_revenue = None
    total_bookings = None
    
    if request.method == 'POST':
        report_type = request.form['report_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Store the report type in session for download
        session['report_type'] = report_type
        session['start_date'] = start_date
        session['end_date'] = end_date
        
        if report_type == 'bookings':
            report_title = "Bookings Report"
            
            # Fetch bookings within date range
            cursor.execute("""
                SELECT b.*, u.username, p.location 
                FROM bookings b 
                JOIN users u ON b.user_id = u.user_id 
                JOIN parking_spots p ON b.spot_id = p.spot_id 
                WHERE DATE(b.start_time) >= %s AND DATE(b.start_time) <= %s
            """, (start_date, end_date))
            
            report_data = cursor.fetchall()
            
        elif report_type == 'revenue':
            report_title = "Revenue Report"
            
            # Fetch daily revenue
            cursor.execute("""
                SELECT DATE(t.transaction_time) as date, 
                       SUM(t.amount) as revenue, 
                       COUNT(t.transaction_id) as bookings
                FROM transactions t
                JOIN bookings b ON t.booking_id = b.booking_id
                WHERE DATE(t.transaction_time) >= %s AND DATE(t.transaction_time) <= %s
                GROUP BY DATE(t.transaction_time)
                ORDER BY DATE(t.transaction_time)
            """, (start_date, end_date))
            
            report_data = cursor.fetchall()
            
            # Calculate totals
            total_revenue = sum(float(item['revenue']) for item in report_data)
            total_bookings = sum(item['bookings'] for item in report_data)
            
        elif report_type == 'occupancy':
            report_title = "Occupancy Report"
            
            # Fetch occupancy by location
            cursor.execute("""
                SELECT p.location, 
                       SUM(TIMESTAMPDIFF(HOUR, b.start_time, b.end_time)) as hours,
                       (SUM(TIMESTAMPDIFF(HOUR, b.start_time, b.end_time)) / 
                        (TIMESTAMPDIFF(DAY, %s, %s) * 24) * 100) as occupancy_rate
                FROM bookings b
                JOIN parking_spots p ON b.spot_id = p.spot_id
                WHERE DATE(b.start_time) >= %s AND DATE(b.end_time) <= %s
                      AND b.status != 'cancelled'
                GROUP BY p.location
            """, (start_date, end_date, start_date, end_date))
            
            report_data = cursor.fetchall()
            
            # Format occupancy rate
            for item in report_data:
                item['occupancy_rate'] = round(float(item['occupancy_rate']), 2)
    
    return render_template('admin/generate_report.html', 
                          report_data=report_data, 
                          report_title=report_title,
                          start_date=start_date,
                          end_date=end_date,
                          report_type=report_type,
                          total_revenue=total_revenue,
                          total_bookings=total_bookings)

# Admin - Download Report
@app.route('/admin/download_report')
def download_report():
    if 'admin_id' not in session or 'report_type' not in session:
        return redirect(url_for('admin_dashboard'))
    
    report_type = session['report_type']
    start_date = session['start_date']
    end_date = session['end_date']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    if report_type == 'bookings':
        # Headers
        csv_writer.writerow(['Booking ID', 'User', 'Location', 'Start Time', 'End Time', 'Status', 'Payment Status'])
        
        # Fetch data
        cursor.execute("""
            SELECT b.booking_id, u.username, p.location, b.start_time, b.end_time, b.status, b.payment_status
            FROM bookings b 
            JOIN users u ON b.user_id = u.user_id 
            JOIN parking_spots p ON b.spot_id = p.spot_id 
            WHERE DATE(b.start_time) >= %s AND DATE(b.start_time) <= %s
        """, (start_date, end_date))
        
        for row in cursor.fetchall():
            csv_writer.writerow([
                row['booking_id'],
                row['username'],
                row['location'],
                row['start_time'],
                row['end_time'],
                row['status'],
                row['payment_status']
            ])
        
        filename = f"bookings_report_{start_date}_to_{end_date}.csv"
    
    elif report_type == 'revenue':
        # Headers
        csv_writer.writerow(['Date', 'Revenue', 'Number of Bookings'])
        
        # Fetch data
        cursor.execute("""
            SELECT DATE(t.transaction_time) as date, 
                   SUM(t.amount) as revenue, 
                   COUNT(t.transaction_id) as bookings
            FROM transactions t
            JOIN bookings b ON t.booking_id = b.booking_id
            WHERE DATE(t.transaction_time) >= %s AND DATE(t.transaction_time) <= %s
            GROUP BY DATE(t.transaction_time)
            ORDER BY DATE(t.transaction_time)
        """, (start_date, end_date))
        
        total_revenue = 0
        total_bookings = 0
        
        for row in cursor.fetchall():
            csv_writer.writerow([
                row['date'],
                row['revenue'],
                row['bookings']
            ])
            total_revenue += float(row['revenue'])
            total_bookings += row['bookings']
        
        # Add total row
        csv_writer.writerow(['Total', total_revenue, total_bookings])
        
        filename = f"revenue_report_{start_date}_to_{end_date}.csv"
    
    elif report_type == 'occupancy':
        # Headers
        csv_writer.writerow(['Location', 'Total Hours', 'Occupancy Rate (%)'])
        
        # Fetch data
        cursor.execute("""
            SELECT p.location, 
                   SUM(TIMESTAMPDIFF(HOUR, b.start_time, b.end_time)) as hours,
                   (SUM(TIMESTAMPDIFF(HOUR, b.start_time, b.end_time)) / 
                    (TIMESTAMPDIFF(DAY, %s, %s) * 24) * 100) as occupancy_rate
            FROM bookings b
            JOIN parking_spots p ON b.spot_id = p.spot_id
            WHERE DATE(b.start_time) >= %s AND DATE(b.end_time) <= %s
                  AND b.status != 'cancelled'
            GROUP BY p.location
        """, (start_date, end_date, start_date, end_date))
        
        for row in cursor.fetchall():
            csv_writer.writerow([
                row['location'],
                row['hours'],
                round(float(row['occupancy_rate']), 2)
            ])
        
        filename = f"occupancy_report_{start_date}_to_{end_date}.csv"
    
    else:
        return redirect(url_for('admin_dashboard'))
    
    # Create response
    output = csv_data.getvalue()
    response = app.response_class(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
    
    return response

# Run the Flask App
if __name__ == '__main__':
    # Initialize database
    from db import initialize_database
    initialize_database()
    
    app.run(debug=True)