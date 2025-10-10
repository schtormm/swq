# CRUD en zoek-stuff 
from auth import current_user, logout
from database import *
from utils import create_display_table, get_cities_list, print_sub_header
from validation import *


def list_users_ui(user_role):
    print_sub_header(f"List {user_role.replace('_', ' ').title()}s")
    
    try:
        users = get_all_users()
        filtered_users = [u for u in users if u['role'] == user_role]
        
        if not filtered_users:
            print(f"No {user_role.replace('_', ' ')}s found.")
            return
        
        headers = ['Username', 'First Name', 'Last Name', 'Registration Date']
        rows = []
        
        for user in filtered_users:
            rows.append([
                user['username'],
                user['first_name'],
                user['last_name'],
                user['registration_date'][:10] if user['registration_date'] else 'N/A'
            ])
        
        print(create_display_table(headers, rows))
        
    except Exception as e:
        print(f"Error listing users: {str(e)}")


def add_user_ui(user_role):
    print_sub_header(f"Add New {user_role.replace('_', ' ').title()}")
    
    try:
        username = get_validated_input("Username (8-10 characters): ", validate_username)
        password = get_validated_input("Password (12-30 characters): ", validate_password)
        first_name = get_validated_input("First Name: ", validate_name, "First Name")
        last_name = get_validated_input("Last Name: ", validate_name, "Last Name")
        
        create_user(username, password, first_name, last_name, user_role)
        print(f"{user_role.replace('_', ' ').title()} created successfully!")
        
    except ValueError as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print("\nUser creation cancelled.")
    except Exception as e:
        print(f"Error creating user: {str(e)}")


def update_user_ui(user_role):
    print_sub_header(f"Update {user_role.replace('_', ' ').title()}")
    
    try:
        username = get_validated_input("Username to update: ", validate_username)
        
        user = get_user_by_username(username)
        if not user:
            print("User not found.")
            return
        
        if user['role'] != user_role:
            print(f"User is not a {user_role.replace('_', ' ')}.")
            return
        
        print(f"\nCurrent details for {username}:")
        print(f"First Name: {user['first_name']}")
        print(f"Last Name: {user['last_name']}")
        
        print("\nEnter new details (press Enter to keep current):")
        
        new_first_name = input(f"First Name [{user['first_name']}]: ")()
        if new_first_name and not validate_name(new_first_name, "First Name")[0]:
            print("Invalid first name.")
            return
        
        new_last_name = input(f"Last Name [{user['last_name']}]: ")()
        if new_last_name and not validate_name(new_last_name, "Last Name")[0]:
            print("Invalid last name.")
            return
        
        updates = {}
        if new_first_name:
            updates['first_name'] = new_first_name
        if new_last_name:
            updates['last_name'] = new_last_name
        
        if updates:
            if update_user(username, **updates):
                print("User updated successfully!")
            else:
                print("Failed to update user.")
        else:
            print("No changes made.")
            
    except KeyboardInterrupt:
        print("\nUpdate cancelled.")
    except Exception as e:
        print(f"Error updating user: {str(e)}")


def delete_user_ui(user_role):
    print_sub_header(f"Delete {user_role.replace('_', ' ').title()}")
    
    try:
        username = get_validated_input("Username to delete: ", validate_username)
        
        user = get_user_by_username(username)
        if not user:
            print("User not found.")
            return
        
        if user['role'] != user_role:
            print(f"User is not a {user_role.replace('_', ' ')}.")
            return
        
        print(f"\nUser to delete: {user['first_name']} {user['last_name']} ({username})")
        confirm = input("Are you sure you want to delete this user? (yes/no): ").lower()
        
        if confirm == 'yes':
            if delete_user(username):
                print("User deleted successfully!")
            else:
                print("Failed to delete user.")
        else:
            print("Deletion cancelled.")
            
    except KeyboardInterrupt:
        print("\nDeletion cancelled.")
    except Exception as e:
        print(f"Error deleting user: {str(e)}")


def reset_user_password_ui(user_role):
    print_sub_header(f"Reset {user_role.replace('_', ' ').title()} Password")
    
    try:
        from utils import generate_temp_password
        
        username = get_validated_input("Username to reset: ", validate_username)
        
        user = get_user_by_username(username)
        if not user:
            print("User not found.")
            return
        
        if user['role'] != user_role:
            print(f"User is not a {user_role.replace('_', ' ')}.")
            return
        
        temp_password = generate_temp_password()
        
        if update_user_password(username, temp_password):
            print("Password reset successfully!")
            print(f"Temporary password: {temp_password}")
            print("Please provide this to the user and advise them to change it immediately.")
        else:
            print("Failed to reset password.")
            
    except KeyboardInterrupt:
        print("\nPassword reset cancelled.")
    except Exception as e:
        print(f"Error resetting password: {str(e)}")


def add_traveller_ui():
    print_sub_header("Add New Traveller")
    
    try:
        print("Enter traveller information:")
        
        first_name = get_validated_input("First Name: ", validate_name, "First Name")
        last_name = get_validated_input("Last Name: ", validate_name, "Last Name")
        birthday = get_validated_input("Birthday (YYYY-MM-DD): ", validate_date, "Birthday")
        gender = get_validated_input("Gender (male/female): ", validate_gender)
        street_name = get_validated_input("Street Name: ", validate_name, "Street Name")
        house_number = get_validated_input("House Number: ", validate_positive_integer, "House Number")
        zip_code = get_validated_input("Zip Code (DDDDXX): ", validate_postcode)
        
        cities = get_cities_list()
        print(f"Available cities: {', '.join(sorted(cities))}")
        city = get_validated_input("City: ", validate_city)
        
        email = get_validated_input("Email: ", validate_email)
        mobile_phone = get_validated_input("Mobile Phone (8 digits only): ", validate_phone_number)
        driving_license = get_validated_input("Driving License (XXDDDDDDD or XDDDDDDDD): ", validate_driving_license)
        
        traveller_data = {
            'first_name': first_name,
            'last_name': last_name,
            'birthday': birthday,
            'gender': gender.lower(),
            'street_name': street_name,
            'house_number': house_number,
            'zip_code': zip_code,
            'city': city,
            'email': email,
            'mobile_phone': mobile_phone,
            'driving_license': driving_license
        }
        
        customer_id = create_traveller(traveller_data)
        print(f"Traveller created successfully! Customer ID: {customer_id}")
        
    except KeyboardInterrupt:
        print("\nTraveller creation cancelled.")
    except Exception as e:
        print(f"Error creating traveller: {str(e)}")


def search_travellers_ui():
    print_sub_header("Search Travellers")
    
    try:
        search_term = get_validated_input("Search term (name, email, or customer ID): ", validate_search_term)
        
        results = search_travellers(search_term)
        
        if not results:
            print("No travellers found matching your search.")
            return
        
        headers = ['ID', 'Customer ID', 'Name', 'Email']
        rows = []
        
        for traveller in results:
            rows.append([
                traveller['id'],
                traveller['customer_id'],
                f"{traveller['first_name']} {traveller['last_name']}",
                traveller['email']
            ])
        
        print(f"\nFound {len(results)} traveller(s):")
        print(create_display_table(headers, rows))
        
    except KeyboardInterrupt:
        print("\nSearch cancelled.")
    except Exception as e:
        print(f"Error searching travellers: {str(e)}")


def update_traveller_ui():
    print_sub_header("Update Traveller")
    
    try:
        search_term = get_validated_input("Search for traveller to update: ", validate_search_term)
        results = search_travellers(search_term)
        
        if not results:
            print("No travellers found.")
            return
        
        if len(results) > 1:
            print(f"Multiple travellers found. Please be more specific.")
            headers = ['ID', 'Customer ID', 'Name', 'Email']
            rows = [[t['id'], t['customer_id'], f"{t['first_name']} {t['last_name']}", t['email']] for t in results]
            print(create_display_table(headers, rows))
            
            traveller_id = get_validated_input("Enter traveller ID to update: ", validate_positive_integer, "Traveller ID")
        else:
            traveller_id = results[0]['id']
        
        traveller = get_traveller_by_id(int(traveller_id))
        if not traveller:
            print("Traveller not found.")
            return
        
        print(f"\nUpdating traveller: {traveller['first_name']} {traveller['last_name']}")
        print("Enter new values (press Enter to keep current):")
        
        updates = {}
        
        new_first_name = input(f"First Name [{traveller['first_name']}]: ")()
        if new_first_name and validate_name(new_first_name, "First Name")[0]:
            updates['first_name'] = new_first_name
        
        new_last_name = input(f"Last Name [{traveller['last_name']}]: ")()
        if new_last_name and validate_name(new_last_name, "Last Name")[0]:
            updates['last_name'] = new_last_name
        
        new_email = input(f"Email [{traveller['email']}]: ")()
        if new_email and validate_email(new_email)[0]:
            updates['email'] = new_email
        
        if updates:
            if update_traveller(traveller['id'], **updates):
                print("Traveller updated successfully!")
            else:
                print("Failed to update traveller.")
        else:
            print("No changes made.")
            
    except KeyboardInterrupt:
        print("\nUpdate cancelled.")
    except Exception as e:
        print(f"Error updating traveller: {str(e)}")


def delete_traveller_ui():
    print_sub_header("Delete Traveller")
    
    try:
        search_term = get_validated_input("Search for traveller to delete: ", validate_search_term)
        results = search_travellers(search_term)
        
        if not results:
            print("No travellers found.")
            return
        
        if len(results) > 1:
            print("Multiple travellers found:")
            headers = ['ID', 'Customer ID', 'Name', 'Email']
            rows = [[t['id'], t['customer_id'], f"{t['first_name']} {t['last_name']}", t['email']] for t in results]
            print(create_display_table(headers, rows))
            
            traveller_id = get_validated_input("Enter traveller ID to delete: ", validate_positive_integer, "Traveller ID")
        else:
            traveller_id = results[0]['id']

        traveller = get_traveller_by_id(int(traveller_id))
        if not traveller:
            print("Traveller not found.")
            return
        
        print(f"\nTraveller to delete:")
        print(f"Name: {traveller['first_name']} {traveller['last_name']}")
        print(f"Customer ID: {traveller['customer_id']}")
        print(f"Email: {traveller['email']}")
        
        confirm = input("\nAre you sure you want to delete this traveller? (yes/no): ").lower()
        
        if confirm == 'yes':
            if delete_traveller(traveller['id']):
                print("Traveller deleted successfully!")
            else:
                print("Failed to delete traveller.")
        else:
            print("Deletion cancelled.")
            
    except KeyboardInterrupt:
        print("\nDeletion cancelled.")
    except Exception as e:
        print(f"Error deleting traveller: {str(e)}")


def add_scooter_ui():
    print_sub_header("Add New Scooter")
    
    try:
        print("Enter scooter information:")
        
        brand = get_validated_input("Brand: ", validate_name, "Brand")
        model = get_validated_input("Model: ", validate_name, "Model")
        serial_number = get_validated_input("Serial Number (10-17 alphanumeric): ", validate_scooter_serial)
        top_speed = get_validated_input("Top Speed (km/h): ", validate_speed, "Top Speed")
        battery_capacity = get_validated_input("Battery Capacity (Wh): ", validate_battery_capacity)
        state_of_charge = get_validated_input("State of Charge (%): ", validate_percentage, "State of Charge")
        target_range_min = get_validated_input("Target Range Min (%): ", validate_percentage, "Target Range Min")
        target_range_max = get_validated_input("Target Range Max (%): ", validate_percentage, "Target Range Max")
        
        print("GPS Coordinates (Rotterdam region, 5 decimal places):")
        latitude = get_validated_input("Latitude (51.80000-52.10000): ", validate_latitude_single)
        longitude = get_validated_input("Longitude (4.20000-4.80000): ", validate_longitude_single)
        mileage = get_validated_input("Mileage (km): ", validate_mileage, "Mileage")
        last_maintenance = input("Last Maintenance Date (YYYY-MM-DD, optional): ")()
        
        if last_maintenance and not validate_date(last_maintenance, "Last Maintenance Date")[0]:
            print("Invalid maintenance date format.")
            return

        scooter_data = {
            'brand': brand,
            'model': model,
            'serial_number': serial_number,
            'top_speed': top_speed,
            'battery_capacity': battery_capacity,
            'state_of_charge': state_of_charge,
            'target_range_min': target_range_min,
            'target_range_max': target_range_max,
            'latitude': latitude,
            'longitude': longitude,
            'mileage': mileage,
            'last_maintenance_date': last_maintenance if last_maintenance else None
        }
        
        create_scooter(scooter_data)
        print("Scooter added successfully!")
        
    except ValueError as e:
        print(f"{str(e)}")
    except KeyboardInterrupt:
        print("\nScooter creation cancelled.")
    except Exception as e:
        print(f"Error creating scooter: {str(e)}")


def search_scooters_ui():
    print_sub_header("Search Scooters")
    
    try:
        search_term = get_validated_input("Search term (brand, model, or serial): ", validate_search_term)
        
        results = search_scooters(search_term)
        
        if not results:
            print("No scooters found matching your search.")
            return
        
        headers = ['ID', 'Brand', 'Model', 'Serial', 'Battery %', 'Status']
        rows = []
        
        for scooter in results:
            status = "Out of Service" if scooter['out_of_service'] else "In Service"
            rows.append([
                scooter['id'],
                scooter['brand'],
                scooter['model'],
                scooter['serial_number'],
                f"{scooter['state_of_charge']}%",
                status
            ])
        
        print(f"\nFound {len(results)} scooter(s):")
        print(create_display_table(headers, rows))
        
    except KeyboardInterrupt:
        print("\nSearch cancelled.")
    except Exception as e:
        print(f"Error searching scooters: {str(e)}")


def update_scooter_ui():
    print_sub_header("Update Scooter")
    
    try:
        search_term = get_validated_input("Search for scooter to update: ", validate_search_term)
        results = search_scooters(search_term)
        
        if not results:
            print("No scooters found.")
            return
        
        if len(results) > 1:
            print("Multiple scooters found:")
            headers = ['ID', 'Brand', 'Model', 'Serial']
            rows = [[s['id'], s['brand'], s['model'], s['serial_number']] for s in results]
            print(create_display_table(headers, rows))
            
            scooter_id = get_validated_input("Enter scooter ID to update: ", validate_positive_integer, "Scooter ID")
        else:
            scooter_id = results[0]['id']
        
        scooter = get_scooter_by_id(int(scooter_id))
        if not scooter:
            print("Scooter not found.")
            return
        
        print(f"\nUpdating scooter: {scooter['brand']} {scooter['model']} ({scooter['serial_number']})")

        if current_user["role"] == "service_engineer":
            print("Service Engineers can update: State of Charge, Target Range, Location, Out-of-Service Status, Mileage, Last Maintenance Date")
        
        print("Enter new values (press Enter to keep current):")
        
        updates = {}
        
        new_soc = input(f"State of Charge % [{scooter['state_of_charge']}]: ")()
        if new_soc and validate_percentage(new_soc)[0]:
            updates['state_of_charge'] = new_soc
        
        # @schtormm misschien even naar kijken, zou massaging van input kunnen zijn
        new_lat = input(f"Latitude [{scooter['latitude']:.5f}]: ")()
        new_lng = input(f"Longitude [{scooter['longitude']:.5f}]: ")()
        if new_lat and new_lng and validate_latitude_single(new_lat) and validate_longitude_single(new_lng)[0]:
            updates['latitude'] = new_lat
            updates['longitude'] = new_lng

        new_target_range_min = input(f"Target Range Min % [{scooter['target_range_min']}]: ")()
        if new_target_range_min and validate_percentage(new_target_range_min)[0]:
            updates['target_range_min'] = new_target_range_min
        
        new_target_range_max = input(f"Target Range Max % [{scooter['target_range_max']}]: ")()
        if new_target_range_max and validate_percentage(new_target_range_max)[0]:
            updates['target_range_max'] = new_target_range_max
        
        new_out_of_service = input(f"Out of Service (y/n) [{scooter['out_of_service']}]: ")()
        if new_out_of_service in ['y', "Y",]:
            updates['out_of_service'] = new_out_of_service == 'y'
        elif new_out_of_service in ['n', 'N']:
            updates['out_of_service'] = new_out_of_service == 'n'
        elif new_out_of_service:
            print("Invalid input for Out of Service. Please enter 'y' or 'n'.")
            return
        
        # net zoals deze
        new_mileage = input(f"Mileage (km) [{scooter['mileage']:.2f}]: ")()
        if new_mileage and validate_mileage(new_mileage)[0]:
            updates['mileage'] = new_mileage
        
        new_last_maintenance = input(f"Last Maintenance Date (YYYY-MM-DD) [{scooter['last_maintenance_date'] if scooter['last_maintenance_date'] else 'N/A'}]: ")()
        if new_last_maintenance:
            if validate_date(new_last_maintenance, "Last Maintenance Date")[0]:
                updates['last_maintenance_date'] = new_last_maintenance
            else:
                print("Invalid date format for Last Maintenance Date.")
                return
        
        # @pablosanderman volgens mij is hier nog extra validatie nodig dat de user ook echt de role heeft, is al functie voor maar wordt hier vgm niet gebruikt
        if current_user["role"] in ["super_admin", "system_admin"]: 
            new_brand = input(f"Brand [{scooter['brand']}]: ")()
            if new_brand and validate_name(new_brand)[0]:
                updates['brand'] = new_brand
                
            new_model = input(f"Model [{scooter['model']}]: ")()
            if new_model and validate_name(new_model)[0]:
                updates['model'] = new_model

            new_serial = input(f"Serial Number [{scooter['serial_number']}]: ")()
            if new_serial and validate_scooter_serial(new_serial)[0]:
                updates['serial_number'] = new_serial

            new_top_speed = input(f"Top Speed (km/h) [{scooter['top_speed']}]: ")()
            if new_top_speed and validate_speed(new_top_speed, "Top Speed")[0]:
                updates['top_speed'] = new_top_speed
            
            new_battery_capacity = input(f"Battery Capacity (Wh) [{scooter['battery_capacity']}]: ")
            if new_battery_capacity and validate_battery_capacity(new_battery_capacity)[0]:
                updates['battery_capacity'] = new_battery_capacity
        else:
            print("You do not have permission to update brand, model, serial number, top speed, or battery capacity.")
            log_event(username=current_user["username"],
                      description=f"Attempted to update scooter {scooter['serial_number']} with ID {scooter['id']} without sufficient permissions.",
                        additional_info=updates,
                        suspicious=True) 
        
        if updates:
            if update_scooter(scooter['id'], **updates):
                print("Scooter updated successfully!")
                log_event(username=current_user["username"],
                          description=f"Updated scooter {scooter['serial_number']} with ID {scooter['id']}.",
                          additional_info=updates,
                          suspicious=False)
            
            else:
                print("Failed to update scooter.")
                log_event(username=current_user["username"],
                          description=f"Failed to update scooter {scooter['serial_number']} with ID {scooter['id']}.",
                          additional_info=updates,
                          suspicious=True)
        else:
            print("No changes made.")
            
    except KeyboardInterrupt:
        print("\nUpdate cancelled.")
    except Exception as e:
        print(f"Error updating scooter: {str(e)}")


def delete_scooter_ui():
    print_sub_header("Delete Scooter")
    
    try:
        search_term = get_validated_input("Search for scooter to delete: ", validate_search_term)
        results = search_scooters(search_term)
        
        if not results:
            print("No scooters found.")
            return
        
        if len(results) > 1:
            print("Multiple scooters found:")
            headers = ['ID', 'Brand', 'Model', 'Serial']
            rows = [[s['id'], s['brand'], s['model'], s['serial_number']] for s in results]
            print(create_display_table(headers, rows))
            
            scooter_id = get_validated_input("Enter scooter ID to delete: ", validate_positive_integer, "Scooter ID")
        else:
            scooter_id = results[0]['id']
        
        scooter = get_scooter_by_id(int(scooter_id))
        if not scooter:
            print("Scooter not found.")
            return
        
        print(f"\nScooter to delete:")
        print(f"Brand/Model: {scooter['brand']} {scooter['model']}")
        print(f"Serial Number: {scooter['serial_number']}")
        
        confirm = input("\nAre you sure you want to delete this scooter? (yes/no): ").lower()
        
        if confirm == 'yes':
            if delete_scooter(scooter['id']):
                print("Scooter deleted successfully!")
            else:
                print("Failed to delete scooter.")
        else:
            print("Deletion cancelled.")
            
    except KeyboardInterrupt:
        print("\nDeletion cancelled.")
    except Exception as e:
        print(f"Error deleting scooter: {str(e)}")


def create_backup_ui():
    print_sub_header("Create System Backup")
    
    try:
        print("Creating system backup...")
        backup_filename = create_backup()
        
        if backup_filename:
            print(f"Backup created successfully: {backup_filename}")
        else:
            print("Failed to create backup.")
            
    except Exception as e:
        print(f"Error creating backup: {str(e)}")


def list_backups_ui():
    print_sub_header("Available Backups")
    
    try:
        backups = list_backups()
        
        if not backups:
            print("No backups found.")
            return
        
        headers = ['Filename', 'Size (bytes)', 'Created']
        rows = []
        
        for backup in backups:
            rows.append([
                backup['filename'],
                backup['size'],
                backup['created'][:19].replace('T', ' ')
            ])
        
        print(create_display_table(headers, rows))
        
    except Exception as e:
        print(f"Error listing backups: {str(e)}")


def restore_backup_ui():
    print_sub_header("Restore from Backup")
    
    try:
        backups = list_backups()
        
        if not backups:
            print("No backups available.")
            return
        
        print("Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['filename']} ({backup['created'][:19].replace('T', ' ')})")
        
        choice = get_validated_input(f"Select backup (1-{len(backups)}): ", validate_positive_integer, "Choice", 1, len(backups))
        selected_backup = backups[int(choice) - 1]
        
        print(f"\nWarning: This will replace the current system with backup: {selected_backup['filename']}")
        confirm = input("Are you sure you want to continue? (yes/no): ").lower()
        
        if confirm == 'yes':
            if restore_backup(selected_backup['filename']):
                print("System restored successfully!")
                logout()
            else:
                print("Failed to restore system.")
        else:
            print("Restore cancelled.")
            
    except KeyboardInterrupt:
        print("\nRestore cancelled.")
    except Exception as e:
        print(f"Error restoring backup: {str(e)}")


def generate_restore_code_ui():
    print_sub_header("Generate Restore Code")
    
    try:
        users = get_all_users()
        sys_admins = [u for u in users if u['role'] == 'system_admin']
        
        if not sys_admins:
            print("No System Administrators found.")
            return
        
        print("System Administrators:")
        for i, admin in enumerate(sys_admins, 1):
            print(f"{i}. {admin['username']} ({admin['first_name']} {admin['last_name']})")
        
        admin_choice = get_validated_input(f"Select administrator (1-{len(sys_admins)}): ", validate_positive_integer, "Choice", 1, len(sys_admins))
        selected_admin = sys_admins[int(admin_choice) - 1]
        
        backups = list_backups()
        if not backups:
            print("No backups available.")
            return
        
        print("\nAvailable backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['filename']} ({backup['created'][:19].replace('T', ' ')})")
        
        backup_choice = get_validated_input(f"Select backup (1-{len(backups)}): ", validate_positive_integer, "Choice", 1, len(backups))
        selected_backup = backups[int(backup_choice) - 1]
        
        code = generate_restore_code_for_admin(selected_admin['username'], selected_backup['filename'])
        
        print(f"\nRestore code generated: {code}")
        print(f"Administrator: {selected_admin['username']}")
        print(f"Backup: {selected_backup['filename']}")
        print("This code can only be used once by the specified administrator.")
        
    except KeyboardInterrupt:
        print("\nCode generation cancelled.")
    except Exception as e:
        print(f"Error generating restore code: {str(e)}")


def list_restore_codes_ui():
    print_sub_header("Active Restore Codes")
    
    try:
        codes = list_restore_codes()
        
        if not codes:
            print("No active restore codes.")
            return
        
        headers = ['Code', 'Administrator', 'Backup File', 'Created']
        rows = []
        
        for code_info in codes:
            rows.append([
                code_info['code'],
                code_info['admin_username'],
                code_info['backup_file'],
                code_info['created'][:19].replace('T', ' ')
            ])
        
        print(create_display_table(headers, rows))
        
    except Exception as e:
        print(f"Error listing restore codes: {str(e)}")


def revoke_restore_code_ui():
    print_sub_header("Revoke Restore Code")
    
    try:
        codes = list_restore_codes()
        
        if not codes:
            print("No active restore codes to revoke.")
            return
        
        print("Active restore codes:")
        for i, code_info in enumerate(codes, 1):
            print(f"{i}. {code_info['code']} (Admin: {code_info['admin_username']}, Backup: {code_info['backup_file']})")
        
        choice = get_validated_input(f"Select code to revoke (1-{len(codes)}): ", validate_positive_integer, "Choice", 1, len(codes))
        selected_code = codes[int(choice) - 1]
        
        confirm = input(f"Revoke code {selected_code['code']}? (yes/no): ").lower()
        
        if confirm == 'yes':
            if revoke_restore_code(selected_code['code']):
                print("Restore code revoked successfully!")
            else:
                print("Failed to revoke restore code.")
        else:
            print("Revocation cancelled.")
            
    except KeyboardInterrupt:
        print("\nRevocation cancelled.")
    except Exception as e:
        print(f"Error revoking restore code: {str(e)}")


def use_restore_code_ui():
    print_sub_header("Use Restore Code")
    
    try:
        code = input("Enter restore code: ")().upper()
        
        if not code:
            print("Restore code cannot be empty.")
            return
        
        success, message = use_restore_code(code, current_user["username"])
        
        if success:
            print(f"{message}")
        else:
            print(f"{message}")
            
    except KeyboardInterrupt:
        print("\nRestore cancelled.")
    except Exception as e:
        print(f"Error using restore code: {str(e)}")


def view_logs_ui(suspicious_only=False):
    log_type = "Suspicious Activities" if suspicious_only else "System Logs"
    print_sub_header(f"View {log_type}")
    
    try:
        logs = get_logs(only_suspicious=suspicious_only, limit=50)
        
        if not logs:
            print(f"No {log_type.lower()} found.")
            return
        
        headers = ['#', 'Date/Time', 'Username', 'Description', 'Suspicious']
        rows = []
        
        for log in logs:
            rows.append([
                log['log_number'],
                log['date_time'][:19].replace('T', ' '),
                log['username'],
                log['description'][:50] + ('...' if len(log['description']) > 50 else ''),
                'Yes' if log['suspicious'] else 'No'
            ])
        
        print(f"Recent {log_type} (showing last {len(logs)} entries):")
        print(create_display_table(headers, rows))
        
        if logs:
            choice = input("\nView details for a specific log entry? (Enter log number or press Enter to continue): ")()
            if choice and choice.isdigit():
                log_num = choice
                selected_log = next((log for log in logs if log['log_number'] == log_num), None)
                if selected_log:
                    print(f"\nLog Entry #{selected_log['log_number']}:")
                    print(f"Date/Time: {selected_log['date_time']}")
                    print(f"Username: {selected_log['username']}")
                    print(f"Description: {selected_log['description']}")
                    print(f"Additional Info: {selected_log['additional_info']}")
                    print(f"Suspicious: {'Yes' if selected_log['suspicious'] else 'No'}")
                else:
                    print("Log entry not found.")
        
    except Exception as e:
        print(f"Error viewing logs: {str(e)}") 