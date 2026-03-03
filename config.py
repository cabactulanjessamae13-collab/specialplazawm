"""
Configuration file for Warranty Management System
"""

import os

# Database Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'warranty_management'

# Flask Configuration
SECRET_KEY = 'warranty_management_secret_key_2026'
SESSION_TYPE = 'filesystem'

# Application Configuration
DEBUG = True
TESTING = False

# Server Configuration
HOST = '127.0.0.1'
PORT = 5000

# Database Connection Parameters
DB_PARAMS = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DB,
    'autocommit': True,
    'use_pure': True
}

# Role Definitions
ROLES = {
    'customer': 'Customer',
    'staff': 'Staff Member',
    'technician': 'Technician',
    'manager': 'Manager'
}

# Page Sizes
ITEMS_PER_PAGE = 20

# Application Features
FEATURES = {
    'customer_portal': True,
    'staff_portal': True,
    'technician_portal': True,
    'manager_dashboard': True,
    'analytics': True,
    'notifications': False,  # Future feature
    'email_alerts': False  # Future feature
}
