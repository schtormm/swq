#!/usr/bin/env python3
# main deel van de applicatie
import os
import sys
from datetime import datetime

from auth import (current_user, initialize_hard_coded_super_admin, login,
                  logout, require_role)
from database import check_suspicious_logs_alert, initialize_database, create_user, get_user_by_username
from encryption import initialize_encryption, is_encryption_initialized
from utils import print_header, print_separator
from view import display_main_menu


def seed_default_users():
    """Seed function to create default users: service engineer and system admin"""
    print("Seeding default users...")
    
    try:
        # Create system admin
        existing_system_admin = get_user_by_username("system_admin")
        if not existing_system_admin:
            create_user(
                username="system_admin",
                password="SysAdmin_456!",
                first_name="System",
                last_name="Administrator",
                role="system_admin"
            )
            print("✓ System Administrator account created: system_admin")
        else:
            print("✓ System Administrator account already exists")
        
        # Create service engineer
        existing_service_engineer = get_user_by_username("service_engineer")
        if not existing_service_engineer:
            create_user(
                username="service_engineer",
                password="Engineer_789@",
                first_name="Service",
                last_name="Engineer",
                role="service_engineer"  
            )
            print("✓ Service Engineer account created: service_engineer")
        else:
            print("✓ Service Engineer account already exists")
            
    except Exception as e:
        print(f"Warning: Could not seed default users: {str(e)}")


def initialize_system():
    print_header("Urban Mobility Backend System")
    print("Initializing system...")
    
    try:
        initialize_encryption()
        print("✓ Encryption system initialized")
        
        initialize_database()
        print("✓ Database initialized")
 
        initialize_hard_coded_super_admin()
        print("✓ Super Administrator account ready")
        
        seed_default_users()
        print("✓ Default users seeded")
        
        print("✓ System initialization complete")
        print_separator()
        
    except Exception as e:
        print(f"System initialization failed: {str(e)}")
        sys.exit(1)


def main():
    """Main application loop"""
    initialize_system()
    
    print("Welcome to Urban Mobility Backend System")
    print("Super Administrator credentials: super_admin / Admin_123?")
    print_separator()
    if is_encryption_initialized():
        while True:
            try:
                if current_user["username"] is None:
                    print("\nPlease login to continue:")
                    if login():
                        if require_role("super_admin" or "system_admin"):
                            check_suspicious_logs_alert()
                        continue
                    else:
                        print("Login failed. Please try again.")
                else:
                    display_main_menu()
                    
            except KeyboardInterrupt:
                print("\n\nShutting down Urban Mobility Backend System...")
                logout()
                break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Please try again or contact system administrator.")


if __name__ == "__main__":
    main() 