"""
Database setup script - Run this to initialize the database
"""

import MySQLdb
from werkzeug.security import generate_password_hash
import sys

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'warranty_management'

def create_database():
    """Create the database if it doesn't exist"""
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.close()
        conn.close()
        print("[✓] Database created successfully")
        return True
    except Exception as e:
        print(f"[✗] Error creating database: {e}")
        return False

def create_tables():
    """Create all required tables"""
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                address VARCHAR(255),
                role ENUM('customer', 'staff', 'technician', 'manager') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                registrations INT DEFAULT 0,
                active_warranties INT DEFAULT 0,
                service_requests INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Appliances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appliances (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                appliance_name VARCHAR(100) NOT NULL,
                brand VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                serial_number VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(50) NOT NULL,
                purchase_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')
        
        # Warranties table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warranties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                appliance_id INT NOT NULL,
                customer_id INT NOT NULL,
                warranty_type ENUM('Manufacturer', 'Extended') DEFAULT 'Manufacturer',
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                coverage VARCHAR(255) NOT NULL,
                status ENUM('Active', 'Expired', 'Inactive') DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE,
                FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')
        
        # Service Requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                appliance_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priority ENUM('low', 'medium', 'high') NOT NULL,
                status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
                technician_id INT,
                technician_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE,
                FOREIGN KEY(technician_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("[✓] All tables created successfully")
        return True
    except Exception as e:
        print(f"[✗] Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data for testing"""
    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("[i] Sample data already exists, skipping insertion")
            cursor.close()
            conn.close()
            return True
        
        # Insert sample users (customers)
        customer_password = generate_password_hash('password123')
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            'john_smith', 'john@customer.com', customer_password, 'John Smith', '+1 234 567 8901', '123 Main St. Springfield', 'customer',
            'sarah_johnson', 'sarah@customer.com', customer_password, 'Sarah Johnson', '+1 234 567 8902', '456 Oak Ave. Springfield', 'customer'
        ))
        
        # Insert sample staff
        staff_password = generate_password_hash('password123')
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('staff_user', 'staff@special.com', staff_password, 'Staff Member', '+1 234 567 8903', '789 Staff Ave', 'staff'))
        
        # Insert sample technicians
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            'tom_anderson', 'tom@technician.com', staff_password, 'Tom Anderson', '+1 234 567 8904', '321 Tech Lane', 'technician',
            'lisa_martinez', 'lisa@technician.com', staff_password, 'Lisa Martinez', '+1 234 567 8905', '654 Service St', 'technician'
        ))
        
        # Insert sample manager
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', ('manager_user', 'manager@special.com', staff_password, 'Manager User', '+1 234 567 8906', '999 Manager Plaza', 'manager'))
        
        # Get customer IDs
        cursor.execute("SELECT id FROM users WHERE role = 'customer'")
        customers = cursor.fetchall()
        customer_ids = [c[0] for c in customers]
        
        # Insert customer records
        for customer_id in customer_ids:
            cursor.execute("INSERT INTO customers (user_id) VALUES (%s)", (customer_id,))
        
        # Insert sample appliances
        cursor.execute('''
            INSERT INTO appliances (customer_id, appliance_name, brand, model, serial_number, category, purchase_date)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            customer_ids[0], 'Refrigerator', 'Samsung', 'RF28R7351SR', 'SN001234567', 'kitchen', '2024-01-15',
            customer_ids[0], 'Washing Machine', 'LG', 'WM9000HVA', 'SN001234568', 'laundry', '2024-03-20',
            customer_ids[1], 'Dishwasher', 'Bosch', 'SHPM88Z75N', 'SN001234569', 'kitchen', '2023-11-10',
            customer_ids[1], 'Air Conditioner', 'Daikin', 'FTXS35LVIU', 'SN001234570', 'climate', '2023-06-05',
            customer_ids[0], 'Microwave Oven', 'Panasonic', 'NN-SN966S', 'SN001234571', 'kitchen', '2025-01-10'
        ))
        
        # Get appliance IDs
        cursor.execute("SELECT id, customer_id FROM appliances")
        appliances = cursor.fetchall()
        
        # Insert sample warranties
        for appliance_id, customer_id in appliances:
            cursor.execute('''
                INSERT INTO warranties (appliance_id, customer_id, warranty_type, start_date, end_date, coverage, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (appliance_id, customer_id, 'Manufacturer', '2024-01-15', '2026-01-15', 'Full parts and labor coverage for 2 years', 'Active'))
        
        # Get technician for assignment
        cursor.execute("SELECT id FROM users WHERE role = 'technician' LIMIT 1")
        tech_id = cursor.fetchone()[0]
        
        # Insert sample service requests
        cursor.execute('''
            INSERT INTO service_requests (customer_id, appliance_id, title, description, priority, status, technician_id, technician_notes)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s),
            (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            customer_ids[0], appliances[0][0], 'Refrigerator not cooling', 'The refrigerator is making noise but not cooling properly', 'high', 'in_progress', tech_id, 'Compressor needs inspection. Scheduled for tomorrow.',
            customer_ids[0], appliances[1][0], 'Washing machine leaking water', 'Water is leaking from the bottom during spin cycle', 'medium', 'completed', tech_id, 'Replaced drain hose seal. Issue resolved.',
            customer_ids[1], appliances[2][0], 'Dishwasher error code', 'Dishwasher displays E24 error code and stops mid-cycle', 'medium', 'pending', None, None
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        print("[✓] Sample data inserted successfully")
        return True
    except Exception as e:
        print(f"[✗] Error inserting sample data: {e}")
        return False

def main():
    """Main function to set up everything"""
    print("=" * 50)
    print("Warranty Management System - Database Setup")
    print("=" * 50)
    
    if not create_database():
        sys.exit(1)
    
    if not create_tables():
        sys.exit(1)
    
    if not insert_sample_data():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("[✓] Database setup completed successfully!")
    print("=" * 50)
    print("\nLogin Credentials:")
    print("- Customer: john@customer.com / password123")
    print("- Staff: staff@special.com / password123")
    print("- Technician: tom@technician.com / password123")
    print("- Manager: manager@special.com / password123")
    print("\nYou can now run: python app.py")

if __name__ == '__main__':
    main()
