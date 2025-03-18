import mysql.connector

# Database Configuration
db_config = {
    'host': 'localhost',      # Replace with your MySQL host
    'user': 'root',           # Replace with your MySQL username
    'password': '',           # Replace with your MySQL password
}

# Create database if it doesn't exist
def create_database():
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS parking_db")
        cursor.close()
        conn.close()
        print("Database 'parking_db' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

# Full configuration with database
full_db_config = {
    **db_config,
    'database': 'parking_db'  # Database name
}

# Get Database Connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**full_db_config)
        print("Database connected successfully!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Initialize Database (Optional)
def initialize_database():
    # First ensure database exists
    create_database()
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        # Create Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Staff Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                staff_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Admins Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Parking Spots Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parking_spots (
                spot_id INT AUTO_INCREMENT PRIMARY KEY,
                location VARCHAR(100) NOT NULL,
                status ENUM('available', 'occupied') DEFAULT 'available',
                price_per_hour DECIMAL(5, 2) NOT NULL
            )
        """)

        # Create Bookings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                spot_id INT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
                payment_status ENUM('paid', 'unpaid') DEFAULT 'unpaid',
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id)
            )
        """)

        # Create Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT NOT NULL,
                payment_method ENUM('cash', 'online') NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
            )
        """)

        # Insert some default parking spots if none exist
        cursor.execute("SELECT COUNT(*) FROM parking_spots")
        spot_count = cursor.fetchone()[0]
        if spot_count == 0:
            cursor.execute("""
                INSERT INTO parking_spots (location, price_per_hour) VALUES 
                ('Section A - Spot 1', 5.00),
                ('Section A - Spot 2', 5.00),
                ('Section B - Spot 1', 4.50),
                ('Section B - Spot 2', 4.50),
                ('Section C - Spot 1', 4.00),
                ('Section C - Spot 2', 4.00)
            """)
            print("Default parking spots created.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
    else:
        print("Failed to initialize database.")

# Test Database Connection
if __name__ == '__main__':
    initialize_database()