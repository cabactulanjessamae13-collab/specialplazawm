# Special Appliance Plaza - Warranty Management System

A comprehensive warranty management platform built with Flask and MySQL.

## Features

- **Customer Portal**: Track warranties, register appliances, submit service requests
- **Staff Portal**: Manage customers, appliances, and warranties
- **Technician Portal**: View assignments and update service request status
- **Manager Dashboard**: Real-time insights and analytics
- **Role-based Access Control**: Different interfaces for different user roles
- **Database Integration**: All data stored securely in MySQL

## System Requirements

- Python 3.8+
- MySQL / XAMPP (with MySQL)
- Flask and dependencies (see requirements.txt)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up MySQL Database

#### Option A: Using the setup script (Recommended)

```bash
python setup_db.py
```

This will:
- Create the `warranty_management` database
- Create all necessary tables
- Insert sample data for testing

#### Option B: Manual Setup in phpMyAdmin

1. Open phpMyAdmin (usually at http://localhost/phpmyadmin)
2. Create a new database named `warranty_management`
3. Import the database schema from the setup_db.py script

### 3. Configure Database Connection

The app is configured to use:
- Host: `localhost`
- User: `root`
- Password: `` (empty)
- Database: `warranty_management`

If your MySQL credentials are different, update them in `app.py`:

```python
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
```

### 4. Run the Application

```bash
python app.py
```

The application will start at: `http://127.0.0.1:5000`

## Default Login Credentials

Use these credentials to test the system:

### Customer
- Email: `john@customer.com`
- Password: `password123`

### Staff Member
- Email: `staff@special.com`
- Password: `password123`

### Technician
- Email: `tom@technician.com`
- Password: `password123`

### Manager
- Email: `manager@special.com`
- Password: `password123`

## Project Structure

```
cabactulan/
├── app.py                          # Main Flask application
├── setup_db.py                     # Database setup script
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── navbar.html                 # Navigation bar
│   ├── index.html                  # Landing page
│   ├── login.html                  # Login page
│   ├── 404.html                    # Not found page
│   ├── 500.html                    # Server error page
│   ├── customer/                   # Customer portal pages
│   │   ├── dashboard.html
│   │   ├── warranties.html
│   │   └── service_requests.html
│   ├── staff/                      # Staff portal pages
│   │   ├── dashboard.html
│   │   ├── customers.html
│   │   ├── appliances.html
│   │   ├── warranties.html
│   │   └── service_requests.html
│   └── technician/                 # Technician portal pages
│       └── assignments.html
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Main stylesheet
│   ├── js/
│   │   └── main.js                 # JavaScript functionality
│   └── images/
│       └── logo.svg                # Company logo
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `password`: Hashed password
- `full_name`: User's full name
- `phone`: Contact number
- `address`: Address
- `role`: User role (customer, staff, technician, manager)
- `created_at`: Timestamp

### Customers Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `registrations`: Count of registered appliances
- `active_warranties`: Count of active warranties
- `service_requests`: Count of service requests

### Appliances Table
- `id`: Primary key
- `customer_id`: Foreign key to customers
- `appliance_name`: Name of the appliance
- `brand`: Brand name
- `model`: Model number
- `serial_number`: Unique serial number
- `category`: Category (kitchen, laundry, climate, other)
- `purchase_date`: Date of purchase

### Warranties Table
- `id`: Primary key
- `appliance_id`: Foreign key to appliances
- `customer_id`: Foreign key to customers
- `warranty_type`: Type (Manufacturer, Extended)
- `start_date`: Warranty start date
- `end_date`: Warranty end date
- `coverage`: Coverage details
- `status`: Status (Active, Expired, Inactive)

### Service Requests Table
- `id`: Primary key
- `customer_id`: Foreign key to customers
- `appliance_id`: Foreign key to appliances
- `title`: Request title
- `description`: Detailed description
- `priority`: Priority level (low, medium, high)
- `status`: Status (pending, in_progress, completed)
- `technician_id`: Assigned technician (optional)
- `technician_notes`: Notes from technician

## API Endpoints

### Authentication
- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

### Customer Portal
- `GET /customer/dashboard` - Customer dashboard
- `GET /customer/warranties` - View warranties
- `GET /customer/service-requests` - View service requests
- `POST /customer/service-request/new` - Create new service request

### Staff Portal
- `GET /staff/dashboard` - Staff dashboard
- `GET /staff/customers` - Customer management
- `POST /staff/customer/add` - Add new customer
- `GET /staff/appliances` - Appliance management
- `POST /staff/appliance/add` - Register appliance
- `GET /staff/warranties` - Warranty management
- `GET /staff/service-requests` - Service request management
- `POST /staff/service-request/assign` - Assign technician

### Technician Portal
- `GET /technician/assignments` - View assignments
- `POST /technician/service-request/<id>/update` - Update service request

### API Routes
- `GET /api/customers` - Get all customers
- `GET /api/appliances/<customer_id>` - Get customer's appliances

## Features Implemented

✅ User authentication with role-based access
✅ Customer warranty tracking
✅ Service request management
✅ Technician assignment system
✅ Staff management tools
✅ Dashboard analytics
✅ Responsive design
✅ Modal dialogs for CRUD operations
✅ Data validation
✅ Database relationships and constraints
✅ User session management
✅ Password hashing (werkzeug security)

## Troubleshooting

### MySQL Connection Error
- Ensure MySQL is running (check XAMPP control panel)
- Verify credentials in `app.py`
- Check database name is `warranty_management`

### Template Not Found Error
- Ensure `templates/` directory exists with all subdirectories
- Clear Flask cache: Delete `__pycache__` folder
- Restart the application

### Static Files Not Loading
- Ensure `static/` directory exists with `css/`, `js/`, and `images/` subdirectories
- Check file paths in CSS and JS files
- Hard refresh browser (Ctrl+Shift+R)

## Security Notes

- Passwords are hashed using werkzeug security
- Session management is implemented
- CSRF protection through Flask sessions
- Role-based access control on all protected routes

## Future Enhancements

- Email notifications
- PDF report generation
- Advanced filtering and search
- Customer payment integration
- SMS notifications
- Warranty expiration alerts
- Service history reports

## Support

For issues or questions, please check:
1. MySQL service is running
2. Database credentials are correct
3. All files are in the correct directories
4. Python version is 3.8 or higher
5. All dependencies are installed from requirements.txt

## License

Special Appliance Plaza - Warranty Management System
Copyright © 2026
# specialplazawm
