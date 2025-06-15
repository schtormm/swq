#!/usr/bin/env python3
"""
Urban Mobility Backend System
Main entry point for the console-based interface
"""

import os
import sys
from datetime import datetime

# Import our modules
from um_auth import login, logout, current_user, initialize_hard_coded_super_admin
from um_database import initialize_database, check_suspicious_logs_alert
from um_ui import display_main_menu
from um_utils import print_header, print_separator
from um_encryption import initialize_encryption


def initialize_system():
    """Initialize the Urban Mobility backend system"""
    print_header("Urban Mobility Backend System")
    print("Initializing system...")
    
    try:
        # Initialize encryption keys
        initialize_encryption()
        print("✓ Encryption system initialized")
        
        # Initialize database
        initialize_database()
        print("✓ Database initialized")
        
        # Initialize hard-coded super administrator
        initialize_hard_coded_super_admin()
        print("✓ Super Administrator account ready")
        
        print("✓ System initialization complete")
        print_separator()
        
    except Exception as e:
        print(f"❌ System initialization failed: {str(e)}")
        sys.exit(1)


def main():
    """Main application loop"""
    initialize_system()
    
    print("Welcome to Urban Mobility Backend System")
    print("Super Administrator credentials: super_admin / Admin_123?")
    print_separator()
    
    while True:
        try:
            if current_user["username"] is None:
                # User is not logged in
                print("\nPlease login to continue:")
                if login():
                    # Check for suspicious activities alert after login
                    if current_user["role"] in ["super_admin", "system_admin"]:
                        check_suspicious_logs_alert()
                    continue
                else:
                    print("Login failed. Please try again.")
            else:
                # User is logged in - display appropriate menu
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