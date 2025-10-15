# views voor menu's
# @pablosanderman deze ook weghalen misschien? of daadwerkelijk gebruiken
from auth import (can_access_logs, can_add_delete_scooters, can_backup_restore,
                  can_manage_role, can_manage_scooters, can_manage_travellers,
                  check_permission, current_user, has_role, logout,
                  require_role)
from ui_functions import *
from utils import (create_display_table, print_header, print_separator,
                   print_sub_header)


def display_main_menu():
    match current_user["role"]:
        case "super_admin":
                super_admin_menu()
        case "system_admin":
                system_admin_menu()
        case "service_engineer":
                service_engineer_menu()
        case default:
            print("Unknown role. Please contact administrator.")
            logout()


def super_admin_menu():
    while True:
        print_header("Super Administrator Menu")
        print(f"Logged in as: {current_user['username']}")
        print_separator()
        print("1. Manage System Administrators")
        print("2. Manage Service Engineers") 
        print("3. Manage Travellers")
        print("4. Manage Scooters")
        print("5. Backup & Restore")
        print("6. Generate Restore Codes")
        print("7. View System Logs")
        print("8. Logout")
        print_separator()
        
        choice = input("Select option (1-8): ")
        
        if choice == "1":
            manage_users_menu("system_admin")
        elif choice == "2":
            manage_users_menu("service_engineer")
        elif choice == "3":
            manage_travellers_menu()
        elif choice == "4":
            manage_scooters_menu()
        elif choice == "5":
            backup_restore_menu()
        elif choice == "6":
            generate_restore_codes_menu()
        elif choice == "7":
            view_logs_menu()
        elif choice == "8":
            logout()
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


def system_admin_menu():
    while True:
        print_header("System Administrator Menu")
        print(f"Logged in as: {current_user['username']}")
        print_separator()
        print("1. Update My Password")
        print("2. Manage Service Engineers")
        print("3. Manage Travellers")
        print("4. Manage Scooters") 
        print("5. Backup & Restore")
        print("6. View System Logs")
        print("7. Logout")
        print_separator()
        
        choice = input("Select option (1-7): ")
        
        if choice == "1":
            update_own_password()
        elif choice == "2":
            manage_users_menu("service_engineer")
        elif choice == "3":
            manage_travellers_menu()
        elif choice == "4":
            manage_scooters_menu()
        elif choice == "5":
            backup_restore_menu()
        elif choice == "6":
            view_logs_menu()
        elif choice == "7":
            logout()
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


def service_engineer_menu():
    while True:
        print_header("Service Engineer Menu")
        print(f"Logged in as: {current_user['username']}")
        print_separator()
        print("1. Update My Password")
        print("2. Update Scooter Information")
        print("3. Search Scooters")
        print("4. Logout")
        print_separator()
        
        choice = input("Select option (1-4): ")
        
        if choice == "1":
            update_own_password()
        elif choice == "2":
            update_scooter_ui()
        elif choice == "3":
            search_scooters_ui()
        elif choice == "4":
            logout()
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


def manage_users_menu(user_role):
    role_name = "System Administrator" if user_role == "system_admin" else "Service Engineer"
    
    while True:
        print_header(f"Manage {role_name}s")
        print("1. List Users")
        print("2. Add New User")
        print("3. Update User")
        print("4. Delete User")
        print("5. Reset User Password")
        print("6. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-6): ")
        
        if choice == "1":
            list_users_ui(user_role)
        elif choice == "2":
            add_user_ui(user_role)
        elif choice == "3":
            update_user_ui(user_role)
        elif choice == "4":
            delete_user_ui(user_role)
        elif choice == "5":
            reset_user_password_ui(user_role)
        elif choice == "6":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "6":
            input("\nPress Enter to continue...")


def manage_travellers_menu():
    while True:
        print_header("Manage Travellers")
        print("1. Add New Traveller")
        print("2. Search Travellers")
        print("3. Update Traveller")
        print("4. Delete Traveller")
        print("5. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-5): ")
        
        if choice == "1":
            add_traveller_ui()
        elif choice == "2":
            search_travellers_ui()
        elif choice == "3":
            update_traveller_ui()
        elif choice == "4":
            delete_traveller_ui()
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "5":
            input("\nPress Enter to continue...")


def manage_scooters_menu():
    while True:
        print_header("Manage Scooters")
        print("1. Add New Scooter")
        print("2. Search Scooters")
        print("3. Update Scooter")
        print("4. Delete Scooter")
        print("5. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-5): ")
        
        if choice == "1":
            if can_add_delete_scooters():
                add_scooter_ui()
            else:
                print("Access denied: You cannot add scooters.")
        elif choice == "2":
            search_scooters_ui()
        elif choice == "3":
            update_scooter_ui()
        elif choice == "4":
            if can_add_delete_scooters():
                delete_scooter_ui()
            else:
                print("Access denied: You cannot delete scooters.")
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "5":
            input("\nPress Enter to continue...")


def backup_restore_menu():
    # i am going to fix this
    while True:
        print_header("Backup & Restore")
        print("1. Create Backup")
        print("2. List Backups")
        print("3. Restore from Backup")
        print("4. Use Restore Code")
        print("5. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-5): ")
        
        if choice == "1":
            create_backup_ui()
        elif choice == "2":
            list_backups_ui()
        elif choice == "3":
            if current_user["role"] == "super_admin":
                restore_backup_ui()
            else:
                print("Access denied: System Administrators must use restore codes.")
        elif choice == "4":
            if current_user["role"] == "system_admin":
                use_restore_code_ui()
            else:
                print("Access denied: System Administrators must use restore codes.")
        elif choice == "5":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "5":
            input("\nPress Enter to continue...")


def generate_restore_codes_menu():
    while True:
        print_header("Restore Code Management")
        print("1. Generate New Restore Code")
        print("2. List Active Restore Codes")
        print("3. Revoke Restore Code")
        print("4. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-4): ")
        
        if choice == "1":
            generate_restore_code_ui()
        elif choice == "2":
            list_restore_codes_ui()
        elif choice == "3":
            revoke_restore_code_ui()
        elif choice == "4":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "4":
            input("\nPress Enter to continue...")


def view_logs_menu():
    while True:
        print_header("System Logs")
        print("1. View Recent Logs")
        print("2. View Suspicious Activities Only")
        print("3. Back to Main Menu")
        print_separator()
        
        choice = input("Select option (1-3): ")
        
        if choice == "1":
            view_logs_ui(suspicious_only=False)
        elif choice == "2":
            view_logs_ui(suspicious_only=True)
        elif choice == "3":
            break
        else:
            print("Invalid option. Please try again.")
        
        if choice != "3":
            input("\nPress Enter to continue...")


def update_own_password():
    print_sub_header("Update Password")
    
    try:
        from database import update_user_password
        from validation import get_validated_input, validate_password

        new_password = get_validated_input(
            "Enter new password: ",
            validate_password
        )
        
        confirm_password = input("Confirm new password: ")
        
        if new_password != confirm_password:
            print("Passwords do not match.")
            return
        
        if update_user_password(current_user["username"], new_password):
            print("Password updated successfully.")
        else:
            print("Failed to update password.")
            
    except KeyboardInterrupt:
        print("\nPassword update cancelled.")
    except Exception as e:
        print(f"Error updating password: {str(e)}")