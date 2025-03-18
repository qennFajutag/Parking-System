# Parking Management System

A full-featured web application for managing parking facilities. This system helps users book parking spots, staff manage parking operations, and administrators monitor the entire system.

## Features

### User Features
- Account registration and management
- Browse and book available parking spots
- View booking history
- Make payments for bookings
- Cancel pending bookings

### Staff Features
- Verify booking details
- Confirm and cancel bookings
- Handle vehicle entry and exit

### Admin Features
- Manage parking spots (add, edit, delete)
- Generate various reports (bookings, revenue, occupancy)
- Export reports as CSV files

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, Jinja2 templates

## Installation and Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd parking-management-system
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flask mysql-connector-python
   ```

4. Configure the database:
   - Edit the database configuration in `db.py` to match your MySQL setup
   - By default, it uses:
     - Host: localhost
     - User: root
     - Password: (blank)
     - Database: parking_db

5. Initialize the database:
   ```
   python db.py
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application:
   - Open a browser and go to `http://localhost:5000`

## Database Structure

The system uses the following database tables:
- users: Regular users who book parking spots
- staff: Staff members who manage daily operations
- admins: Administrators who oversee the entire system
- parking_spots: Information about available parking locations
- bookings: Records of parking spot reservations
- transactions: Payment records for bookings

## Usage

### User Workflow
1. Register an account or login
2. Browse available parking spots
3. Book a spot with start and end times
4. Make payment for the booking
5. Use the parking spot during reserved time

### Staff Workflow
1. Login as staff
2. Verify bookings by ID
3. Confirm or cancel bookings
4. Handle vehicle entry/exit

### Admin Workflow
1. Login as admin
2. Manage parking spots
3. Generate and download reports
4. Monitor system performance

## Security Notes

- For production use, replace the secret key in `app.py` with a secure value
- Implement proper password hashing (the current system stores passwords in plaintext for simplicity)
- Set up HTTPS for secure communications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- [Your Name] - Initial development
