@echo off
REM Warranty Management System - Setup and Run Script

echo.
echo ======================================
echo Warranty Management System Setup
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    exit /b 1
)

echo [OK] pip found
echo.

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    exit /b 1
)

echo [OK] Requirements installed
echo.

REM Setup database
echo Setting up database...
python setup_db.py

if errorlevel 1 (
    echo [ERROR] Failed to setup database
    exit /b 1
)

echo [OK] Database setup complete
echo.

REM Start the application
echo ======================================
echo Starting Warranty Management System
echo ======================================
echo.
echo Access the application at:
echo http://127.0.0.1:5000
echo.
echo Default Credentials:
echo - Customer: john@customer.com / password123
echo - Staff: staff@special.com / password123
echo - Technician: tom@technician.com / password123
echo.

python app.py

pause
