# Complete Installation Guide

## Warranty Management System - Full Setup Instructions

A comprehensive guide to install and run the Special Appliance Plaza Warranty Management System.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Setup](#system-setup)
3. [Installation Steps](#installation-steps)
4. [Database Setup](#database-setup)
5. [Application Launch](#application-launch)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements
- Computer with 1GB+ RAM
- 100MB free disk space
- Windows, macOS, or Linux OS

### Software Requirements
- **Python 3.8 or higher** - [Download](https://www.python.org/downloads/)
- **MySQL 5.7+** or **XAMPP** (includes MySQL) - [Download XAMPP](https://www.apachefriends.org/)
- **Web Browser** (Chrome, Firefox, Safari, or Edge)

---

## System Setup

### Step 1: Install Python

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"

**macOS:**
```bash
# Using Homebrew (install Homebrew first if needed)
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### Step 2: Install XAMPP (or MySQL)

**Option A: XAMPP (Easiest - Includes MySQL)**

1. Download from https://www.apachefriends.org/
2. Install in default location
3. Open XAMPP Control Panel
4. Click "Start" for MySQL

**Option B: MySQL Standalone**

1. Download from https://dev.mysql.com/downloads/mysql/
2. Install following the installer
3. Start MySQL service

### Verify MySQL is Running

**Windows:**
- XAMPP Control Panel should show MySQL as "Running"

**macOS/Linux:**
```bash
mysql --version  # Should show version number
```

---

## Installation Steps

### Step 1: Download/Extract Application Files

Download the `cabactulan` folder and place it in a convenient location:
- Windows: `C:\xampp\cabactulan\` (recommended)
- macOS: `~/Applications/cabactulan/`
- Linux: `/opt/cabactulan/` or `~/cabactulan/`

### Step 2: Open Terminal/Command Prompt

**Windows:**
1. Press `Win + R`
2. Type `cmd`
3. Press Enter

**macOS:**
1. Press `Cmd + Space`
2. Type `Terminal`
3. Press Enter

**Linux:**
Open your terminal application

### Step 3: Navigate to Application Directory

```bash
# Windows
cd C:\xampp\cabactulan

# macOS/Linux
cd ~/cabactulan
```

### Step 4: Verify Python Installation

```bash
python --version
# or
python3 --version
```

Should show: `Python 3.8.x` or higher

### Step 5: Check Health of System

```bash
python health_check.py
```

This will verify:
- ✓ Python version
- ✓ All directories exist
- ✓ All required files present
- ✓ MySQL is running
- ✓ Python packages are installed

---

## Database Setup

### Automatic Setup (Recommended)

#### Windows:
```bash
python setup_db.py
```

#### macOS/Linux:
```bash
python3 setup_db.py
```

**Expected Output:**
```
==================================================
Warranty Management System - Database Setup
==================================================
[✓] Database created successfully
[✓] All tables created successfully
[✓] Sample data inserted successfully

==================================================
[✓] Database setup completed successfully!
==================================================

Login Credentials:
- Customer: john@customer.com / password123
- Staff: staff@special.com / password123
- Technician: tom@technician.com / password123
- Manager: manager@special.com / password123

You can now run: python app.py
```

### Manual Setup (If Automatic Fails)

1. Open phpMyAdmin: http://localhost/phpmyadmin
2. In the left panel, click on "New"
3. Create database named: `warranty_management`
4. Click on the new database
5. Click "Import" tab
6. Copy each SQL statement from setup_db.py and paste it
7. Click "Go"

---

## Application Launch

### Easiest Method (Windows)

Double-click `run.bat` in the cabactulan folder

Or in command prompt:
```bash
run.bat
```

### Easiest Method (macOS/Linux)

```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
pip install -r requirements.txt
python app.py
```

### Expected Output

```
WARNING: This is a development server. Do not use it in a production deployment.
Use a production WSGI server instead.
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

## Access the Application

### Open in Web Browser

Go to: **http://127.0.0.1:5000**

You should see:
- Special Appliance Plaza logo
- "Warranty Management Made Simple" heading
- "Get Started" button

### Login

Click "Get Started" and use one of these credentials:

| Role | Email | Password |
|------|-------|----------|
| Customer | john@customer.com | password123 |
| Staff | staff@special.com | password123 |
| Technician | tom@technician.com | password123 |
| Manager | manager@special.com | password123 |

---

## Verification

### Test the Application

1. **Login as a Customer**
   - Go to Dashboard
   - View your 3 appliances
   - View your 3 warranties
   - View service requests

2. **Go to Staff Portal**
   - Logout first
   - Login as staff@special.com
   - View customer management
   - Add a new customer
   - Assign a technician to a request

3. **Go to Technician Portal**
   - Logout and login as tom@technician.com
   - View your assignments
   - Update the status of a request

### Check Database

Open phpMyAdmin: http://localhost/phpmyadmin

1. Select `warranty_management` database
2. You should see 5 tables:
   - users (6 records)
   - customers (2 records)
   - appliances (5 records)
   - warranties (5 records)
   - service_requests (3 records)

---

## Stopping the Application

Press `Ctrl + C` in the terminal/command prompt

---

## Troubleshooting

### Error: "Can't connect to MySQL server"

**Solution:**
1. Open XAMPP Control Panel
2. Click "Start" for MySQL
3. Wait 5 seconds
4. Run the application again

### Error: "Address already in use"

**Solution (Windows):**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Solution (macOS/Linux):**
```bash
lsof -i :5000
kill -9 <PID>
```

### Error: "No module named 'flask'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "TemplateNotFound"

**Solution:**
1. Make sure you're in the `cabactulan` directory
2. Delete `__pycache__` folder
3. Clear browser cache (Ctrl+Shift+Delete)
4. Restart the application

### Error: "Unknown database"

**Solution:**
```bash
python setup_db.py
```

### MySQL Won't Start

**Windows (XAMPP):**
1. Open XAMPP Control Panel as Administrator
2. Click "Config" button for MySQL
3. Note the port number (usually 3306)
4. Click "Start"

**macOS:**
```bash
brew services restart mysql
```

**Linux:**
```bash
sudo systemctl start mysql
```

---

## File Structure

```
cabactulan/
├── 📄 app.py                    # Main Flask application
├── 📄 setup_db.py               # Database setup
├── 📄 config.py                 # Configuration settings
├── 📄 requirements.txt           # Python dependencies
├── 📄 health_check.py           # System verification
├── 📄 run.bat                   # Windows startup script
├── 📄 run.sh                    # macOS/Linux startup script
├── 📄 README.md                 # Full documentation
├── 📄 QUICK_START.md            # Quick start guide
├── 📄 TESTING_GUIDE.md          # Testing procedures
├── 📄 INSTALLATION.md           # This file
│
├── 📁 templates/                # HTML templates
│   ├── base.html               # Base HTML template
│   ├── index.html              # Landing page
│   ├── login.html              # Login page
│   ├── navbar.html             # Navigation bar
│   ├── 404.html                # 404 error page
│   ├── 500.html                # 500 error page
│   ├── 📁 customer/            # Customer pages
│   │   ├── dashboard.html      # Customer dashboard
│   │   ├── warranties.html     # Warranty list
│   │   └── service_requests.html # Service requests
│   ├── 📁 staff/               # Staff pages
│   │   ├── dashboard.html      # Staff dashboard
│   │   ├── customers.html      # Customer management
│   │   ├── appliances.html     # Appliance management
│   │   ├── warranties.html     # Warranty management
│   │   └── service_requests.html # Service request management
│   └── 📁 technician/          # Technician pages
│       └── assignments.html    # My assignments
│
└── 📁 static/                  # Static files
    ├── 📁 css/
    │   └── style.css           # Main CSS styling
    ├── 📁 js/
    │   └── main.js             # JavaScript functionality
    └── 📁 images/
        └── logo.svg            # Company logo
```

---

## Quick Reference

### Common Commands

```bash
# Start the application
python app.py

# Run health check
python health_check.py

# Initialize database
python setup_db.py

# Install Python packages
pip install -r requirements.txt

# Stop the application
Ctrl + C
```

### Login Credentials (After Setup)

```
Customer:  john@customer.com / password123
Staff:     staff@special.com / password123
Tech:      tom@technician.com / password123
Manager:   manager@special.com / password123
```

### Important URLs

```
Landing:    http://127.0.0.1:5000/
Login:      http://127.0.0.1:5000/login
Dashboard:  http://127.0.0.1:5000/customer/dashboard (logged in)
```

---

## Next Steps

1. **Explore the application** - Try all features
2. **Read the documentation** - See README.md for detailed info
3. **Run the tests** - Check TESTING_GUIDE.md
4. **Customize the application** - Modify colors, add features
5. **Migrate your data** - Import real customer/warranty data

---

## Support and Help

### If You Encounter Issues

1. **Check health_check.py**
   ```bash
   python health_check.py
   ```

2. **Review TESTING_GUIDE.md** - Detailed testing procedures

3. **Check README.md** - Comprehensive documentation

4. **Verify MySQL is running** - Check XAMPP Control Panel

5. **Clear browser cache** - Ctrl+Shift+Delete

---

## System Requirements Summary

| Component | Requirement |
|-----------|------------|
| Python | 3.8+ |
| MySQL | 5.7+ |
| RAM | 1GB+ |
| Disk Space | 100MB |
| Browser | Modern (2020+) |

---

## Security Information

✅ **Password Hashing:** Werkzeug security module
✅ **Session Management:** Flask sessions
✅ **Error Handling:** Comprehensive error pages
✅ **Input Validation:** All forms validated
✅ **Database Security:** SQL injection protection

---

## Performance Information

- Page load time: < 1 second
- Database queries: Optimized
- User sessions: Persistent
- Responsive design: All screen sizes
- Mobile friendly: Yes
- Dark mode support: (Can be added)

---

## License and Terms

This application is provided as-is for the Special Appliance Plaza warranty management system.

---

## Congratulations! 🎉

You've successfully installed the Warranty Management System!

Start exploring and managing warranties like never before.

**Need help?** Check the README.md or QUICK_START.md files.
