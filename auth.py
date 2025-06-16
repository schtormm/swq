"""
Urban Mobility Backend System - authentication en authorization
"""

from datetime import datetime

import bcrypt

from database import create_user, get_user_by_username, log_event
from utils import print_header, print_sub_header
from validation import validate_password, validate_username

current_user = {"username": None, "role": None, "user_id": None}

# hard coded want moet van opdracht
SUPER_ADMIN_USERNAME = "super_admin"
SUPER_ADMIN_PASSWORD = "Admin_123?"

login_attempts = {}
MAX_LOGIN_ATTEMPTS = 3


def initialize_hard_coded_super_admin():
    """Initialize the hard-coded super administrator account"""
    try:
        existing_user = get_user_by_username(SUPER_ADMIN_USERNAME)
        if not existing_user:
            create_user(
                username=SUPER_ADMIN_USERNAME,
                password=SUPER_ADMIN_PASSWORD,
                first_name="Super",
                last_name="Administrator", 
                role="super_admin"
            )
            print(f"Hard-coded Super Administrator account created: {SUPER_ADMIN_USERNAME}")
    except Exception as e:
        print(f"Warning: Could not initialize Super Administrator: {str(e)}")


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hashed_password):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def check_login_attempts(username):
    """Check if user has exceeded maximum login attempts"""
    if username in login_attempts:
        attempts, last_attempt = login_attempts[username]
        # reset ratelimit na 5 minuten
        time_diff = (datetime.now() - last_attempt).total_seconds()
        if time_diff > 300:  # 5 minutes
            del login_attempts[username]
            return True
        return attempts < MAX_LOGIN_ATTEMPTS
    return True


def record_login_attempt(username, success=False):
    """Record login attempt for rate limiting"""
    if not success:
        if username in login_attempts:
            attempts, _ = login_attempts[username]
            login_attempts[username] = (attempts + 1, datetime.now())
        else:
            login_attempts[username] = (1, datetime.now())
    else:
        if username in login_attempts:
            del login_attempts[username]


def login():
    """Handle user login with security measures"""
    print_sub_header("User Login")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Username: ").strip().lower()
            if not username:
                print("❌ Username cannot be empty")
                continue
                
            if not check_login_attempts(username):
                print("❌ Too many failed login attempts. Please try again later.")
                log_event(
                    username=username,
                    description="Login blocked due to too many failed attempts",
                    additional_info=f"Attempt from login system",
                    suspicious=True
                )
                return False
            
            password = input("Password: ")
            if not password:
                print("❌ Password cannot be empty")
                continue
            
            user = get_user_by_username(username)
            if user and verify_password(password, user['password']):
                current_user["username"] = user["username"]
                current_user["role"] = user["role"]
                current_user["user_id"] = user["id"]
                
                record_login_attempt(username, success=True)

                log_event(
                    username=username,
                    description="Successful login",
                    additional_info=f"Role: {user['role']}",
                    suspicious=False
                )
                
                print(f"✅ Login successful! Welcome {user['first_name']} {user['last_name']}")
                print(f"Role: {user['role'].replace('_', ' ').title()}")
                return True
            else:
                record_login_attempt(username, success=False)
                
                log_event(
                    username=username if user else "unknown",
                    description="Failed login attempt",
                    additional_info=f"Username: {username}",
                    suspicious=True if attempt > 0 else False
                )
                
                print("❌ Invalid username or password")
                
                if attempt < max_attempts - 1:
                    print(f"Please try again. ({max_attempts - attempt - 1} attempts remaining)")
                
        except KeyboardInterrupt:
            print("\nLogin cancelled.")
            return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            
            
    print("❌ Maximum login attempts exceeded.")
    return False


def logout():
    """Handle user logout"""
    if current_user["username"]:
        username = current_user["username"]
        log_event(
            username=username,
            description="User logged out",
            additional_info="Normal logout",
            suspicious=False
        )
        print(f"Goodbye {username}!")
    
    current_user["username"] = None
    current_user["role"] = None
    current_user["user_id"] = None


def check_permission(required_roles):
    """
    RBAC dingetje
    Gebruikt decorator om te checken of user de juiste rol heeft
    Args:
        required_roles: List of roles that can access the function

    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if current_user["role"] in required_roles:
                return func(*args, **kwargs)
            else:
                print("❌ Access denied: Insufficient permissions")
                
                username = current_user["username"] if current_user["username"] else "Unknown"
                role = current_user["role"] if current_user["role"] else "None"
                
                log_event(
                    username=username,
                    description="Unauthorized access attempt",
                    additional_info=f"Required: {required_roles}, Current role: {role}, Function: {func.__name__}",
                    suspicious=True
                )
                return None
        return wrapper
    return decorator


def require_role(*roles):
    """
    Simple role requirement check
    Args:
        roles: Roles that are allowed
    Returns:
        True if user has required role, False otherwise
    """
    return current_user["role"] in roles


def is_logged_in():
    """Check if user is currently logged in"""
    return current_user["username"] is not None


def get_current_user():
    """Get current user information"""
    return current_user.copy()


def has_role(role):
    """Check if current user has specific role"""
    return current_user["role"] == role


def can_manage_role(target_role):
    """
    Check if current user can manage accounts of target role
    Super Admin can manage System Admins and Service Engineers
    System Admin can manage Service Engineers only
    Service Engineers cannot manage any accounts
    """
    current_role = current_user["role"]
    
    if current_role == "super_admin":
        return target_role in ["system_admin", "service_engineer"]
    elif current_role == "system_admin":
        return target_role == "service_engineer"
    else:
        return False


def can_access_logs():
    return current_user["role"] in ["super_admin", "system_admin"]


def can_backup_restore():
    return current_user["role"] in ["super_admin", "system_admin"]


def can_manage_travellers():
    return current_user["role"] in ["super_admin", "system_admin"]


def can_manage_scooters():
    return current_user["role"] in ["super_admin", "system_admin", "service_engineer"]


def can_add_delete_scooters():
    return current_user["role"] in ["super_admin", "system_admin"]


def get_role_hierarchy():
    return {
        "super_admin": "Super Administrator",
        "system_admin": "System Administrator", 
        "service_engineer": "Service Engineer"
    } 