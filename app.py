from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'warranty_management_secret_key_2026'
Session(app)
    
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'warranty_management'

mysql = MySQL(app)

# Custom Jinja2 filters
@app.template_filter('date_format')
def format_date(date_obj):
    if isinstance(date_obj, str):
        return date_obj
    if date_obj:
        return date_obj.strftime('%m/%d/%Y')
    return 'N/A'

@app.template_filter('datetime_format')
def format_datetime(dt_obj):
    if isinstance(dt_obj, str):
        return dt_obj
    if dt_obj:
        return dt_obj.strftime('%m/%d/%Y %H:%M')
    return 'N/A'

@app.template_filter('title')
def title_filter(text):
    return text.replace('_', ' ').title()

# ==================== DATABASE INITIALIZATION

def init_db():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
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
            scheduled_date DATE,
            scheduled_time TIME,
            customer_confirmed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE,
            FOREIGN KEY(technician_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Service Schedules table - available time slots set by manager
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_request_id INT NOT NULL,
            schedule_date DATE NOT NULL,
            schedule_time TIME NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(service_request_id) REFERENCES service_requests(id) ON DELETE CASCADE
        )
    ''')
    
    # Appliance Defects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appliance_defects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            appliance_id INT NOT NULL,
            defect_description TEXT NOT NULL,
            severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
            status ENUM('pending', 'under_review', 'repair', 'replace', 'resolved') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY(appliance_id) REFERENCES appliances(id) ON DELETE CASCADE
        )
    ''')
    
    # Defect Decisions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_decisions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            defect_id INT NOT NULL,
            manager_id INT NOT NULL,
            decision ENUM('repair', 'replace') NOT NULL,
            decision_notes TEXT,
            estimated_cost DECIMAL(10,2),
            decision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(defect_id) REFERENCES appliance_defects(id) ON DELETE CASCADE,
            FOREIGN KEY(manager_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Service Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_request_id INT NOT NULL,
            customer_id INT NOT NULL,
            rating INT NOT NULL,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(service_request_id) REFERENCES service_requests(id) ON DELETE CASCADE,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    ''')
    
    # Technician Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technician_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_request_id INT NOT NULL,
            customer_id INT NOT NULL,
            technician_id INT NOT NULL,
            rating INT NOT NULL,
            comments TEXT,
            tip_amount DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(service_request_id) REFERENCES service_requests(id) ON DELETE CASCADE,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY(technician_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Appliance Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appliance_sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            staff_id INT NOT NULL,
            customer_id INT NOT NULL,
            appliance_name VARCHAR(100) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            sale_price DECIMAL(10,2) NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(staff_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    ''')
    
    # Staff Bonuses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff_bonuses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            staff_id INT NOT NULL,
            sale_id INT,
            bonus_type ENUM('sale', 'service') NOT NULL,
            bonus_amount DECIMAL(10,2) NOT NULL,
            description VARCHAR(255),
            status ENUM('pending', 'approved', 'paid') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(staff_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(sale_id) REFERENCES appliance_sales(id) ON DELETE SET NULL
        )
    ''')
    
    # Bonus Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bonus_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bonus_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default bonus settings if not exists
    cursor.execute('SELECT COUNT(*) as count FROM bonus_settings')
    if cursor.fetchone()['count'] == 0:
        cursor.execute('INSERT INTO bonus_settings (bonus_amount) VALUES (0)')
    
    mysql.connection.commit()
    cursor.close()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'customer':
            return redirect(url_for('customer_dashboard'))
        elif role == 'technician':
            return redirect(url_for('technician_assignments'))
        else:
            return redirect(url_for('staff_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND role = %s', (email, role))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            
            if role == 'customer':
                return redirect(url_for('customer_dashboard'))
            elif role == 'technician':
                return redirect(url_for('technician_assignments'))
            else:
                return redirect(url_for('staff_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Email validation function
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

# ==================== CUSTOMER PORTAL ROUTES ====================

@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    customer_id = customer['id'] if customer else None
    
    cursor.execute('SELECT COUNT(*) as count FROM appliances WHERE customer_id = %s', (customer_id,))
    registered_appliances = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM warranties WHERE customer_id = %s AND status = "Active"', (customer_id,))
    active_warranties = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM service_requests WHERE customer_id = %s', (customer_id,))
    service_requests = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT sr.*, a.appliance_name, a.brand, u.full_name as technician_name
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        LEFT JOIN users u ON sr.technician_id = u.id
        WHERE sr.customer_id = %s
        ORDER BY sr.created_at DESC
        LIMIT 3
    ''', (customer_id,))
    recent_requests = cursor.fetchall()
    
    cursor.execute('''
        SELECT a.*, COUNT(DISTINCT w.id) as warranty_count
        FROM appliances a
        LEFT JOIN warranties w ON a.id = w.appliance_id
        WHERE a.customer_id = %s
        GROUP BY a.id
        LIMIT 3
    ''', (customer_id,))
    appliances = cursor.fetchall()
    
    cursor.close()
    
    return render_template('customer/dashboard.html', 
                         registered_appliances=registered_appliances,
                         active_warranties=active_warranties,
                         service_requests=service_requests,
                         recent_requests=recent_requests,
                         appliances=appliances)

@app.route('/customer/warranties')
def customer_warranties():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    customer_id = customer['id'] if customer else None
    
    cursor.execute('''
        SELECT w.*, a.appliance_name, a.brand, a.model, a.serial_number
        FROM warranties w
        JOIN appliances a ON w.appliance_id = a.id
        WHERE w.customer_id = %s
        ORDER BY w.start_date DESC
    ''', (customer_id,))
    warranties = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/warranties.html', warranties=warranties)

@app.route('/customer/service-requests')
def customer_service_requests():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    customer_id = customer['id'] if customer else None
    
    cursor.execute('''
        SELECT sr.*, a.appliance_name, a.brand, 
               t.full_name as technician_name, t.phone as technician_phone
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        LEFT JOIN users t ON sr.technician_id = t.id
        WHERE sr.customer_id = %s
        ORDER BY sr.created_at DESC
    ''', (customer_id,))
    requests = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/service_requests.html', requests=requests)

@app.route('/customer/service-request/new', methods=['POST'])
def create_service_request():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404
        
        customer_id = customer['id']
        
        appliance_id = request.form.get('appliance_id')
        title = request.form.get('title')
        priority = request.form.get('priority')
        description = request.form.get('description')
        
        if not all([appliance_id, title, priority, description]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        cursor.execute('''
            INSERT INTO service_requests (customer_id, appliance_id, title, description, priority)
            VALUES (%s, %s, %s, %s, %s)
        ''', (customer_id, appliance_id, title, description, priority))
        mysql.connection.commit()
        
        return redirect(url_for('customer_service_requests'))
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()

# Customer defect reporting
@app.route('/customer/defects')
def customer_defects():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    customer_id = customer['id'] if customer else None
    
    cursor.execute('''
        SELECT d.*, a.appliance_name, a.brand, a.model
        FROM appliance_defects d
        JOIN appliances a ON d.appliance_id = a.id
        WHERE d.customer_id = %s
        ORDER BY d.created_at DESC
    ''', (customer_id,))
    defects = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/defects.html', defects=defects)

@app.route('/customer/defect/new', methods=['POST'])
def create_defect():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404
        
        customer_id = customer['id']
        
        appliance_id = request.form.get('appliance_id')
        defect_description = request.form.get('defect_description')
        severity = request.form.get('severity')
        
        if not all([appliance_id, defect_description, severity]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        cursor.execute('''
            INSERT INTO appliance_defects (customer_id, appliance_id, defect_description, severity)
            VALUES (%s, %s, %s, %s)
        ''', (customer_id, appliance_id, defect_description, severity))
        mysql.connection.commit()
        
        return redirect(url_for('customer_defects'))
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()

# Customer feedback
@app.route('/customer/feedback')
def customer_feedback():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    customer_id = customer['id'] if customer else None
    
    # Get completed service requests for feedback
    cursor.execute('''
        SELECT sr.id, sr.title, a.appliance_name, a.brand, sr.technician_id
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        WHERE sr.customer_id = %s AND sr.status = 'completed'
        ORDER BY sr.updated_at DESC
    ''', (customer_id,))
    completed_requests = cursor.fetchall()
    
    cursor.close()
    
    return render_template('customer/feedback.html', completed_requests=completed_requests)

@app.route('/customer/feedback/service', methods=['POST'])
def submit_service_feedback():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
        customer = cursor.fetchone()
        customer_id = customer['id'] if customer else None
        
        service_request_id = request.form.get('service_request_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        
        if not all([service_request_id, rating]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        cursor.execute('''
            INSERT INTO service_feedback (service_request_id, customer_id, rating, comments)
            VALUES (%s, %s, %s, %s)
        ''', (service_request_id, customer_id, rating, comments))
        mysql.connection.commit()
        
        return redirect(url_for('customer_feedback'))
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()

@app.route('/customer/feedback/technician', methods=['POST'])
def submit_technician_feedback():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
        customer = cursor.fetchone()
        customer_id = customer['id'] if customer else None
        
        service_request_id = request.form.get('service_request_id')
        technician_id = request.form.get('technician_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        tip_amount = request.form.get('tip_amount', 0)
        
        if not all([service_request_id, technician_id, rating]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        cursor.execute('''
            INSERT INTO technician_feedback (service_request_id, customer_id, technician_id, rating, comments, tip_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (service_request_id, customer_id, technician_id, rating, comments, tip_amount))
        
        # Create bonus record for technician if tip > 0
        if tip_amount and float(tip_amount) > 0:
            cursor.execute('''
                INSERT INTO staff_bonuses (staff_id, bonus_type, bonus_amount, description, status)
                VALUES (%s, 'service', %s, 'Tip from customer', 'pending')
            ''', (technician_id, tip_amount))
        
        mysql.connection.commit()
        
        return redirect(url_for('customer_feedback'))
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()

# ==================== STAFF PORTAL ROUTES ====================

@app.route('/staff/dashboard')
def staff_dashboard():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT COUNT(*) as count FROM customers')
    total_customers = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM appliances')
    total_appliances = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM warranties WHERE status = "Active"')
    active_warranties = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM service_requests WHERE status IN ("pending", "in_progress")')
    pending_requests = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT u.full_name, u.email, u.phone, c.created_at
        FROM customers c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
        LIMIT 2
    ''')
    recent_customers = cursor.fetchall()
    
    cursor.execute('''
        SELECT sr.id, sr.title, sr.priority, sr.status, a.brand, u.full_name, sr.created_at
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        JOIN users u ON sr.customer_id = u.id
        WHERE sr.technician_id IS NULL
        ORDER BY sr.created_at DESC
        LIMIT 2
    ''')
    pending_service_requests = cursor.fetchall()
    
    cursor.close()
    
    return render_template('staff/dashboard.html',
                         total_customers=total_customers,
                         total_appliances=total_appliances,
                         active_warranties=active_warranties,
                         pending_requests=pending_requests,
                         recent_customers=recent_customers,
                         pending_service_requests=pending_service_requests)

@app.route('/staff/customers')
def staff_customers():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT u.*, c.id as customer_id, c.registrations, c.active_warranties, c.service_requests
        FROM users u
        JOIN customers c ON u.id = c.user_id
        ORDER BY u.full_name
    ''')
    customers = cursor.fetchall()
    cursor.close()
    
    return render_template('staff/customers.html', customers=customers)

@app.route('/staff/customer/add', methods=['POST'])
def add_customer():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    password = request.form.get('password')
    
    # Validate email format
    if not is_valid_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format. Please enter a valid email address (e.g., john@example.com)'}), 400
    
    username = email.split('@')[0]
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (username, email, hashed_password, full_name, phone, address, 'customer'))
        
        user_id = cursor.lastrowid
        cursor.execute('INSERT INTO customers (user_id) VALUES (%s)', (user_id,))
        mysql.connection.commit()
        
        return redirect(url_for('staff_customers'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/staff/customer/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    # Validate email format
    if not is_valid_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format. Please enter a valid email address (e.g., john@example.com)'}), 400
    
    try:
        # Get the user_id from customers table
        cursor.execute('SELECT user_id FROM customers WHERE id = %s', (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404
        
        user_id = customer['user_id']
        
        # Update user information
        cursor.execute('''
            UPDATE users 
            SET full_name = %s, email = %s, phone = %s, address = %s
            WHERE id = %s
        ''', (full_name, email, phone, address, user_id))
        
        mysql.connection.commit()
        
        return redirect(url_for('staff_customers'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/staff/appliances')
def staff_appliances():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT a.*, u.full_name as customer_name, c.id as customer_id
        FROM appliances a
        JOIN customers c ON a.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY a.created_at DESC
    ''')
    appliances = cursor.fetchall()
    
    cursor.execute('''
        SELECT c.id, u.full_name, u.email
        FROM customers c
        JOIN users u ON c.user_id = u.id
        ORDER BY u.full_name
    ''')
    customers = cursor.fetchall()
    cursor.close()
    
    return render_template('staff/appliances.html', appliances=appliances, customers=customers)

@app.route('/staff/appliance/add', methods=['POST'])
def add_appliance():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    customer_id = request.form.get('customer_id')
    appliance_name = request.form.get('appliance_name')
    brand = request.form.get('brand')
    model = request.form.get('model')
    serial_number = request.form.get('serial_number')
    category = request.form.get('category')
    purchase_date = request.form.get('purchase_date')
    
    try:
        cursor.execute('''
            INSERT INTO appliances (customer_id, appliance_name, brand, model, serial_number, category, purchase_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (customer_id, appliance_name, brand, model, serial_number, category, purchase_date))
        mysql.connection.commit()
        
        return redirect(url_for('staff_appliances'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/staff/add', methods=['POST'])
def add_staff():
    if 'user_id' not in session or session.get('role') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    password = request.form.get('password')
    
    username = email.split('@')[0]
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (username, email, hashed_password, full_name, phone, address, 'staff'))
        
        mysql.connection.commit()
        
        return redirect(url_for('staff_dashboard'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/technician/add', methods=['POST'])
def add_technician():
    if 'user_id' not in session or session.get('role') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    password = request.form.get('password')
    
    username = email.split('@')[0]
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (username, email, hashed_password, full_name, phone, address, 'technician'))
        
        mysql.connection.commit()
        
        return redirect(url_for('staff_dashboard'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/staff/warranties')
def staff_warranties():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT w.*, a.appliance_name, a.brand, a.model, u.full_name as customer_name
        FROM warranties w
        JOIN appliances a ON w.appliance_id = a.id
        JOIN customers c ON w.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY w.start_date DESC
    ''')
    warranties = cursor.fetchall()
    cursor.close()
    
    return render_template('staff/warranties.html', warranties=warranties)

@app.route('/staff/service-requests')
def staff_service_requests():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT sr.*, a.appliance_name, a.brand, u.full_name as customer_name, t.full_name as technician_name
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        JOIN customers c ON sr.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        LEFT JOIN users t ON sr.technician_id = t.id
        ORDER BY sr.created_at DESC
    ''')
    requests = cursor.fetchall()
    
    cursor.execute('SELECT id, full_name FROM users WHERE role = "technician" ORDER BY full_name')
    technicians = cursor.fetchall()
    cursor.close()
    
    return render_template('staff/service_requests.html', requests=requests, technicians=technicians)

@app.route('/staff/service-request/assign', methods=['POST'])
def assign_technician():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    request_id = request.form.get('request_id')
    technician_id = request.form.get('technician_id')
    
    try:
        cursor.execute('''
            UPDATE service_requests
            SET technician_id = %s, status = 'in_progress'
            WHERE id = %s
        ''', (technician_id, request_id))
        mysql.connection.commit()
        
        return redirect(url_for('staff_service_requests'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# ==================== SCHEDULE MANAGEMENT ROUTES ====================

@app.route('/api/service-schedules/<int:request_id>', methods=['GET'])
def get_service_schedules(request_id):
    """Get available schedules for a service request"""
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get schedules for this service request
    cursor.execute('''
        SELECT ss.id, ss.service_request_id, ss.schedule_date, ss.is_available,
               DATE_FORMAT(ss.schedule_date, '%%Y-%%m-%%d') as date_str,
               TIME_FORMAT(ss.schedule_time, '%%H:%%i') as time_str
        FROM service_schedules ss
        WHERE ss.service_request_id = %s AND ss.is_available = TRUE
        ORDER BY ss.schedule_date, ss.schedule_time
    ''', (request_id,))
    schedules = cursor.fetchall()
    cursor.close()
    
    # Convert to JSON serializable format
    result = []
    for s in schedules:
        result.append({
            'id': s['id'],
            'service_request_id': s['service_request_id'],
            'date_str': s['date_str'],
            'time_str': s['time_str']
        })
    
    return jsonify(result)

@app.route('/staff/service-request/set-schedule', methods=['POST'])
def set_service_schedule():
    """Staff/Manager sets available time slots for a service request (Mon-Sat only)"""
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        request_id = request.form.get('request_id')
        schedule_dates = request.form.getlist('schedule_date[]')
        schedule_times = request.form.getlist('schedule_time[]')
        
        if not request_id or not schedule_dates or not schedule_times:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Clear existing schedules for this request
        cursor.execute('DELETE FROM service_schedules WHERE service_request_id = %s', (request_id,))
        
        # Add new schedules (Mon-Sat only, no Sundays)
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for date_str, time_str in zip(schedule_dates, schedule_times):
            if date_str and time_str:
                # Validate it's not Sunday
                schedule_date = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = schedule_date.strftime('%A')
                
                if day_name in days_of_week:
                    schedule_time = datetime.strptime(time_str, '%H:%M').time()
                    cursor.execute('''
                        INSERT INTO service_schedules (service_request_id, schedule_date, schedule_time, is_available)
                        VALUES (%s, %s, %s, TRUE)
                    ''', (request_id, date_str, schedule_time))
        
        mysql.connection.commit()
        
        return redirect(url_for('staff_service_requests'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/customer/service-request/confirm-schedule', methods=['POST'])
def confirm_service_schedule():
    """Customer confirms their preferred schedule"""
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        request_id = request.form.get('request_id')
        schedule_id = request.form.get('schedule_id')
        
        if not request_id or not schedule_id:
            return redirect(url_for('customer_service_requests'))
        
        # Get the selected schedule
        cursor.execute('''
            SELECT schedule_date, schedule_time 
            FROM service_schedules 
            WHERE id = %s AND service_request_id = %s AND is_available = TRUE
        ''', (schedule_id, request_id))
        schedule = cursor.fetchone()
        
        if not schedule:
            return redirect(url_for('customer_service_requests'))
        
        # Update service request with confirmed schedule
        cursor.execute('''
            UPDATE service_requests 
            SET scheduled_date = %s, scheduled_time = %s, customer_confirmed = TRUE
            WHERE id = %s
        ''', (schedule['schedule_date'], schedule['schedule_time'], request_id))
        
        # Mark the selected schedule as unavailable (others remain available)
        cursor.execute('UPDATE service_schedules SET is_available = FALSE WHERE id = %s', (schedule_id,))
        
        mysql.connection.commit()
        
        return redirect(url_for('customer_service_requests'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# Staff sales and bonuses
@app.route('/staff/sales')
def staff_sales():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('''
        SELECT s.*, u.full_name as customer_name, st.full_name as staff_name
        FROM appliance_sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        JOIN users st ON s.staff_id = st.id
        ORDER BY s.sale_date DESC
    ''')
    sales = cursor.fetchall()
    
    cursor.execute('SELECT c.id, u.full_name, u.email FROM customers c JOIN users u ON c.user_id = u.id ORDER BY u.full_name')
    customers = cursor.fetchall()
    
    # Calculate total sales
    cursor.execute('SELECT COALESCE(SUM(sale_price), 0) as total FROM appliance_sales')
    total_sales = cursor.fetchone()['total']
    
    # Calculate today's sales
    cursor.execute("SELECT COALESCE(SUM(sale_price), 0) as total FROM appliance_sales WHERE DATE(sale_date) = CURDATE()")
    today_sales = cursor.fetchone()['total']
    
    cursor.close()
    
    return render_template('staff/sales.html', sales=sales, customers=customers, total_sales=total_sales, today_sales=today_sales)

@app.route('/staff/sale/add', methods=['POST'])
def add_sale():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    customer_id = request.form.get('customer_id')
    appliance_name = request.form.get('appliance_name')
    brand = request.form.get('brand')
    model = request.form.get('model')
    sale_price = request.form.get('sale_price')
    
    try:
        cursor.execute('''
            INSERT INTO appliance_sales (staff_id, customer_id, appliance_name, brand, model, sale_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (session['user_id'], customer_id, appliance_name, brand, model, sale_price))
        
        sale_id = cursor.lastrowid
        
        # Get bonus percentage from settings (default 10%)
        cursor.execute('SELECT bonus_amount FROM bonus_settings LIMIT 1')
        bonus_settings = cursor.fetchone()
        # Get bonus amount from settings (manager inputs fixed amount per sale)
        bonus_amount = float(bonus_settings['bonus_amount']) if bonus_settings and bonus_settings['bonus_amount'] else 0
        cursor.execute('''
            INSERT INTO staff_bonuses (staff_id, sale_id, bonus_type, bonus_amount, description, status)
            VALUES (%s, %s, 'sale', %s, 'New appliance sale bonus', 'pending')
        ''', (session['user_id'], sale_id, bonus_amount))
        
        mysql.connection.commit()
        
        return redirect(url_for('staff_sales'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

@app.route('/staff/bonuses')
def staff_bonuses():
    if 'user_id' not in session or session.get('role') not in ['staff', 'manager']:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if session.get('role') == 'manager':
        cursor.execute('''
            SELECT b.*, u.full_name as staff_name
            FROM staff_bonuses b
            JOIN users u ON b.staff_id = u.id
            ORDER BY b.created_at DESC
        ''')
    else:
        cursor.execute('''
            SELECT b.*, u.full_name as staff_name
            FROM staff_bonuses b
            JOIN users u ON b.staff_id = u.id
            WHERE b.staff_id = %s
            ORDER BY b.created_at DESC
        ''', (session['user_id'],))
    
    bonuses = cursor.fetchall()
    
    # Get bonus settings
    cursor.execute('SELECT * FROM bonus_settings LIMIT 1')
    bonus_settings = cursor.fetchone()
    
    cursor.close()
    
    return render_template('staff/bonuses.html', bonuses=bonuses, bonus_settings=bonus_settings)

@app.route('/staff/bonus/approve/<int:bonus_id>', methods=['POST'])
def approve_bonus(bonus_id):
    if 'user_id' not in session or session.get('role') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute('UPDATE staff_bonuses SET status = "approved" WHERE id = %s', (bonus_id,))
        mysql.connection.commit()
        
        return redirect(url_for('staff_bonuses'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# Manager sales overview
@app.route('/manager/sales')
def manager_sales():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('''
        SELECT s.*, u.full_name as customer_name, st.full_name as staff_name,
               b.bonus_amount as bonus_amount
        FROM appliance_sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        JOIN users st ON s.staff_id = st.id
        LEFT JOIN staff_bonuses b ON b.sale_id = s.id AND b.bonus_type = 'sale'
        ORDER BY s.sale_date DESC
    ''')
    sales = cursor.fetchall()
    
    cursor.execute('SELECT COALESCE(SUM(sale_price), 0) as total FROM appliance_sales')
    total_sales = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(SUM(sale_price), 0) as total FROM appliance_sales WHERE DATE(sale_date) = CURDATE()")
    today_sales = cursor.fetchone()['total']
    
    cursor.execute('SELECT * FROM bonus_settings LIMIT 1')
    bonus_settings = cursor.fetchone()
    
    cursor.close()
    
    return render_template('manager/sales.html', 
                         sales=sales, 
                         total_sales=total_sales, 
                         today_sales=today_sales,
                         bonus_settings=bonus_settings)

@app.route('/manager/bonus/settings', methods=['POST'])
def update_bonus_settings():
    if 'user_id' not in session or session.get('role') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    bonus_amount = request.form.get('bonus_amount')
    
    try:
        cursor.execute('SELECT COUNT(*) as count FROM bonus_settings')
        count = cursor.fetchone()['count']
        
        if count == 0:
            cursor.execute('INSERT INTO bonus_settings (bonus_amount) VALUES (%s)', (bonus_amount,))
        else:
            cursor.execute('UPDATE bonus_settings SET bonus_amount = %s', (bonus_amount,))
        
        mysql.connection.commit()
        
        return redirect(url_for('manager_sales'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# Manager defect decisions
@app.route('/manager/defects')
def manager_defects():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('''
        SELECT d.*, a.appliance_name, a.brand, a.model, u.full_name as customer_name,
               dd.decision, dd.decision_notes, dd.estimated_cost, dd.decision_date,
               m.full_name as manager_name
        FROM appliance_defects d
        JOIN appliances a ON d.appliance_id = a.id
        JOIN customers c ON d.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        LEFT JOIN defect_decisions dd ON d.id = dd.defect_id
        LEFT JOIN users m ON dd.manager_id = m.id
        ORDER BY d.created_at DESC
    ''')
    defects = cursor.fetchall()
    
    cursor.close()
    
    return render_template('manager/defects.html', defects=defects)

# Manager feedback view
@app.route('/manager/feedback')
def manager_feedback():
    if 'user_id' not in session or session.get('role') != 'manager':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get service feedback
    cursor.execute('''
        SELECT sf.id, sf.rating, sf.comments, sf.created_at,
               sr.title as service_title, a.appliance_name, a.brand,
               u.full_name as customer_name,
               'service' as feedback_type
        FROM service_feedback sf
        JOIN service_requests sr ON sf.service_request_id = sr.id
        JOIN appliances a ON sr.appliance_id = a.id
        JOIN customers c ON sf.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY sf.created_at DESC
    ''')
    service_feedback = cursor.fetchall()
    
    # Get technician feedback
    cursor.execute('''
        SELECT tf.id, tf.rating, tf.comments, tf.tip_amount, tf.created_at,
               sr.title as service_title, a.appliance_name, a.brand,
               u.full_name as customer_name,
               t.full_name as technician_name,
               'technician' as feedback_type
        FROM technician_feedback tf
        JOIN service_requests sr ON tf.service_request_id = sr.id
        JOIN appliances a ON sr.appliance_id = a.id
        JOIN customers c ON tf.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        LEFT JOIN users t ON tf.technician_id = t.id
        ORDER BY tf.created_at DESC
    ''')
    technician_feedback = cursor.fetchall()
    
    cursor.close()
    
    return render_template('manager/feedback.html', 
                         service_feedback=service_feedback,
                         technician_feedback=technician_feedback)

@app.route('/manager/defect/decision', methods=['POST'])
def make_defect_decision():
    if 'user_id' not in session or session.get('role') != 'manager':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    defect_id = request.form.get('defect_id')
    decision = request.form.get('decision')
    decision_notes = request.form.get('decision_notes')
    estimated_cost = request.form.get('estimated_cost')
    
    try:
        cursor.execute('''
            INSERT INTO defect_decisions (defect_id, manager_id, decision, decision_notes, estimated_cost)
            VALUES (%s, %s, %s, %s, %s)
        ''', (defect_id, session['user_id'], decision, decision_notes, estimated_cost))
        
        cursor.execute('''
            UPDATE appliance_defects SET status = %s, updated_at = NOW() WHERE id = %s
        ''', (decision, defect_id))
        
        mysql.connection.commit()
        
        return redirect(url_for('manager_defects'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# ==================== TECHNICIAN PORTAL ROUTES ====================

@app.route('/technician/assignments')
def technician_assignments():
    if 'user_id' not in session or session.get('role') != 'technician':
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT COUNT(*) as count FROM service_requests WHERE technician_id = %s AND status = "pending"', (session['user_id'],))
    pending = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM service_requests WHERE technician_id = %s AND status = "in_progress"', (session['user_id'],))
    in_progress = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM service_requests WHERE technician_id = %s AND status = "completed"', (session['user_id'],))
    completed = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT sr.*, a.appliance_name, a.brand, u.full_name as customer_name, u.phone, u.email
        FROM service_requests sr
        JOIN appliances a ON sr.appliance_id = a.id
        JOIN customers c ON sr.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE sr.technician_id = %s
        ORDER BY sr.priority DESC, sr.created_at DESC
    ''', (session['user_id'],))
    assignments = cursor.fetchall()
    
    cursor.close()
    
    return render_template('technician/assignments.html',
                         pending=pending,
                         in_progress=in_progress,
                         completed=completed,
                         assignments=assignments)

@app.route('/technician/service-request/<int:request_id>/update', methods=['POST'])
def update_service_request(request_id):
    if 'user_id' not in session or session.get('role') != 'technician':
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    try:
        cursor.execute('''
            UPDATE service_requests
            SET status = %s, technician_notes = %s, updated_at = NOW()
            WHERE id = %s AND technician_id = %s
        ''', (status, notes, request_id, session['user_id']))
        mysql.connection.commit()
        
        return redirect(url_for('technician_assignments'))
    except Exception as e:
        mysql.connection.rollback()
        return redirect(url_for('customer_service_requests'))
    finally:
        cursor.close()

# ==================== API ROUTES ====================

@app.route('/api/customers', methods=['GET'])
def api_get_customers():
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT c.id, u.full_name, u.email
        FROM customers c
        JOIN users u ON c.user_id = u.id
        ORDER BY u.full_name
    ''')
    customers = cursor.fetchall()
    cursor.close()
    
    return jsonify(customers)

@app.route('/api/appliances/<int:customer_id>', methods=['GET'])
def api_get_appliances(customer_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT id, appliance_name, brand, model
        FROM appliances
        WHERE customer_id = %s
        ORDER BY appliance_name
    ''', (customer_id,))
    appliances = cursor.fetchall()
    cursor.close()
    
    return jsonify(appliances)


@app.route('/api/my-appliances', methods=['GET'])
def api_get_my_appliances():
    if 'user_id' not in session or session.get('role') != 'customer':
        return jsonify({'success': False}), 401
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT id FROM customers WHERE user_id = %s', (session['user_id'],))
    customer = cursor.fetchone()
    
    if not customer:
        cursor.close()
        return jsonify([])
    
    # Get appliances EXCLUDING those where manager decided to "replace"
    # Only show appliances that do not have a "replace" decision from manager
    cursor.execute('''
        SELECT a.id, a.appliance_name, a.brand, a.model
        FROM appliances a
        WHERE a.customer_id = %s
        AND a.id NOT IN (
            SELECT ad.appliance_id 
            FROM appliance_defects ad
            JOIN defect_decisions dd ON ad.id = dd.defect_id
            WHERE dd.decision = 'replace'
        )
        ORDER BY a.appliance_name
    ''', (customer['id'],))
    appliances = cursor.fetchall()
    cursor.close()
    
    return jsonify(appliances)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
    # specialplazawm
