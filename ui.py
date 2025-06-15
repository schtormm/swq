from auth import current_user, check_permission, logout
from utils import bulletted_display, print_header
from validation import *
import database


def display_menu():
    role = current_user["role"]
    if role == "super_admin":
        super_admin_menu()
    elif role == "system_admin":
        system_admin_menu()
    elif role == "consultant":
        consultant_menu()
    else:
        print("Unknown role.")


def super_admin_menu():
    while True:
        print_header("Super Administrator Menu")
        print("1. Update Password")
        print("2. Manage System Administrators")
        print("3. Manage Consultants")
        print("4. Manage Members")
        print("5. Backup and Restore")
        print("6. View Logs")
        print("7. Logout")
        choice = input("Select an option: ")

        if choice == "1":
            update_password()
        elif choice == "2":
            manage_system_administrators()
        elif choice == "3":
            manage_consultants()
        elif choice == "4":
            manage_members()
        elif choice == "5":
            backup_and_restore()
        elif choice == "6":
            view_logs()
        elif choice == "7":
            logout()
            break
        else:
            print("Option not implemented yet.")


def system_admin_menu():
    while True:
        print_header("System Administrator Menu")
        print("1. Update Password")
        print("2. Manage Consultants")
        print("3. Manage Members")
        print("4. Backup and Restore")
        print("5. View Logs")
        print("6. Logout")
        choice = input("Select an option: ")

        if choice == "1":
            update_password()
        elif choice == "2":
            manage_consultants()
        elif choice == "3":
            manage_members()
        elif choice == "4":
            backup_and_restore()
        elif choice == "5":
            view_logs()
        elif choice == "6":
            logout()
            break
        else:
            print("Option not implemented yet.")


def consultant_menu():
    while True:
        print_header("Consultant Menu")
        print("1. Update Password")
        print("2. Add Member")
        print("3. Update Member")
        print("4. Search Member")
        print("5. Logout")
        choice = input("Select an option: ")

        if choice == "1":
            update_password()
        elif choice == "2":
            add_member()
        elif choice == "3":
            update_member()
        elif choice == "4":
            search_member()
        elif choice == "5":
            logout()
            break
        else:
            print("Option not implemented yet.")


def manage_system_administrators():
    pass


def update_password():
    pass


def manage_consultants():
    while True:
        print_header("Manage Consultants")
        print("1. Add Consultant")
        print("2. Update Consultant")
        print("3. Delete Consultant")
        print("4. Reset Consultant Password")
        print("5. Back")
        choice = input("Select an option: ")

        if choice == "1":
            add_consultant()
        elif choice == "2":
            update_consultant()
        elif choice == "3":
            delete_consultant()
        elif choice == "4":
            reset_consultant_password()
        elif choice == "5":
            break
        else:
            print("Option not implemented yet.")


def add_consultant():
    pass


def update_consultant():
    pass


def delete_consultant():
    pass


def reset_consultant_password():
    pass


def manage_members():
    while True:
        print_header("Manage Members")
        print("1. Add Member")
        print("2. Update Member")
        print("3. Delete Member")
        print("4. Search Member")
        print("5. Back")
        choice = input("Select an option: ")

        if choice == "1":
            add_member()
        elif choice == "2":
            update_member()
        elif choice == "3":
            delete_member()
        elif choice == "4":
            search_member()
        elif choice == "5":
            break
        else:
            print("Option not implemented yet.")


@check_permission("consultant", "system_admin", "super_admin")
def add_member():
    print_header("Add New Member")

    first_name = get_valid_string(
        "Enter first name: ", NAME_PATTERN, max_length=50)
    last_name = get_valid_string(
        "Enter last name: ", NAME_PATTERN, max_length=50)
    age = get_valid_integer("Enter age: ", min_value=0, max_value=120)
    gender = get_valid_gender("Enter gender")
    weight = get_valid_float("Enter weight in kg: ",
                             min_value=0, max_value=500)
    street_name = get_valid_string(
        "Enter street name: ", NAME_PATTERN, max_length=100)
    house_number = get_valid_integer(
        "Enter house number: ", min_value=1, max_value=10000
    )
    zip_code = get_valid_zip_code("Enter zip code (DDDDCC): ")
    city = get_valid_city("Enter city: ")
    email = get_valid_email("Enter email address: ")
    mobile_phone = get_valid_phone(
        "Enter mobile phone number (+31-6-DDDDDDDD): ")

    # Call the database function to add the member
    database.add_member(
        first_name=first_name,
        last_name=last_name,
        age=age,
        gender=gender,
        weight=weight,
        street_name=street_name,
        house_number=house_number,
        zip_code=zip_code,
        city=city,
        email=email,
        mobile_phone=mobile_phone,
    )

    print("Member added successfully!")


@check_permission("consultant", "system_admin", "super_admin")
def update_member():
    pass


@check_permission("system_admin", "super_admin")
def delete_member():
    pass


@check_permission("consultant", "system_admin", "super_admin")
def search_member():
    print("\nSearch Member")
    search_term = get_valid_string("Enter search term: ", SEARCH_PATTERN)

    import time
    start_time = time.time()

    matching_members = database.search_members(search_term)

    end_time = time.time()
    search_time = end_time - start_time

    if matching_members:
        print("Matching Members:")
        print(bulletted_display(matching_members))
    else:
        print("No matching members found.")

    print(f"\nSearch term: '{search_term}'")
    print(f"Found {len(matching_members)} matches")
    print(f"Search time: {search_time:.3f} seconds")


def backup_and_restore():
    pass


def view_logs():
    pass
