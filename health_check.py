"""
System Health Check Script
Verifies that all components are properly installed and configured
"""

import sys
import os

def check_python():
    """Check Python version"""
    print("[*] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"    [✓] Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print(f"    [✗] Python 3.8+ required (found {version.major}.{version.minor})")
        return False

def check_directories():
    """Check required directories"""
    print("\n[*] Checking directory structure...")
    required_dirs = [
        'templates',
        'templates/customer',
        'templates/staff',
        'templates/technician',
        'static',
        'static/css',
        'static/js',
        'static/images'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"    [✓] {dir_name}/")
        else:
            print(f"    [✗] {dir_name}/ NOT FOUND")
            all_exist = False
    
    return all_exist

def check_files():
    """Check required files"""
    print("\n[*] Checking required files...")
    required_files = [
        'app.py',
        'setup_db.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'QUICK_START.md',
        'TESTING_GUIDE.md',
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/navbar.html',
        'templates/customer/dashboard.html',
        'templates/customer/warranties.html',
        'templates/customer/service_requests.html',
        'templates/staff/dashboard.html',
        'templates/staff/customers.html',
        'templates/staff/appliances.html',
        'templates/staff/warranties.html',
        'templates/staff/service_requests.html',
        'templates/technician/assignments.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    all_exist = True
    for file_name in required_files:
        if os.path.isfile(file_name):
            print(f"    [✓] {file_name}")
        else:
            print(f"    [✗] {file_name} NOT FOUND")
            all_exist = False
    
    return all_exist

def check_packages():
    """Check installed Python packages"""
    print("\n[*] Checking Python packages...")
    required_packages = {
        'flask': 'Flask',
        'flask_mysqldb': 'Flask-MySQLdb',
        'flask_session': 'Flask-Session',
        'werkzeug': 'Werkzeug'
    }
    
    all_installed = True
    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print(f"    [✓] {display_name} installed")
        except ImportError:
            print(f"    [✗] {display_name} NOT INSTALLED")
            print(f"       Run: pip install -r requirements.txt")
            all_installed = False
    
    return all_installed

def check_mysql():
    """Check MySQL availability"""
    print("\n[*] Checking MySQL connection...")
    try:
        import MySQLdb
        try:
            conn = MySQLdb.connect(
                host='localhost',
                user='root',
                password='',
                db='warranty_management'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            print(f"    [✓] MySQL connected (Found {count} users in database)")
            return True
        except MySQLdb.Error as e:
            if 'Unknown database' in str(e):
                print("    [✗] Database 'warranty_management' not found")
                print("       Run: python setup_db.py")
            else:
                print(f"    [✗] MySQL error: {e}")
                print("       Ensure MySQL is running in XAMPP Control Panel")
            return False
    except ImportError:
        print("    [!] MySQLdb not installed")
        print("       Run: pip install -r requirements.txt")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("Warranty Management System - Health Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python),
        ("Directories", check_directories),
        ("Files", check_files),
        ("Python Packages", check_packages),
        ("MySQL Database", check_mysql)
    ]
    
    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()
    
    print("\n" + "=" * 60)
    print("Health Check Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "[✓] PASS" if passed else "[✗] FAIL"
        print(f"{check_name}: {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n[✓] All checks passed! Ready to run the application.")
        print("\nStart the application with:")
        print("  - Windows: run.bat")
        print("  - Mac/Linux: ./run.sh")
        print("  - Manual: python app.py")
        return 0
    else:
        print("\n[✗] Some checks failed. Please fix the issues above.")
        print("\nFor help, see QUICK_START.md or TESTING_GUIDE.md")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
