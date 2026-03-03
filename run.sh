#!/bin/bash

# Warranty Management System - Setup and Run Script

echo ""
echo "======================================"
echo "Warranty Management System Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not available"
    exit 1
fi

echo "[OK] pip3 found"
echo ""

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install requirements"
    exit 1
fi

echo "[OK] Requirements installed"
echo ""

# Setup database
echo "Setting up database..."
python3 setup_db.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to setup database"
    exit 1
fi

echo "[OK] Database setup complete"
echo ""

# Start the application
echo "======================================"
echo "Starting Warranty Management System"
echo "======================================"
echo ""
echo "Access the application at:"
echo "http://127.0.0.1:5000"
echo ""
echo "Default Credentials:"
echo "- Customer: john@customer.com / password123"
echo "- Staff: staff@special.com / password123"
echo "- Technician: tom@technician.com / password123"
echo ""

python3 app.py
