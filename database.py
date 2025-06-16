import hashlib
import json
import os
import sqlite3
import zipfile
from contextlib import closing
from datetime import date, datetime

from encryption import (decrypt_data, decrypt_log_data, encrypt_data,
                        encrypt_log_data)
from um_utils import (format_datetime, generate_customer_id,
                      generate_restore_code)

# config zooi
DB_FILE = "urban_mobility.db"
LOG_FILE = "um_system.log"
BACKUP_DIR = "backups"

# Restore codes storage (in production this would be in database)
restore_codes = {}  # {code: {admin_username: str, backup_file: str, created: datetime}}


def get_db_connection():
    """Get database connection with row factory for easier access"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username_hash TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    password_hash BLOB NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS travellers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    birthday TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    street_name TEXT NOT NULL,
                    house_number TEXT NOT NULL,
                    zip_code TEXT NOT NULL,
                    city TEXT NOT NULL,
                    email TEXT NOT NULL,
                    mobile_phone TEXT NOT NULL,
                    driving_license TEXT NOT NULL,
                    registration_date TEXT NOT NULL,
                    search_index TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scooters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    serial_number TEXT UNIQUE NOT NULL,
                    top_speed INTEGER NOT NULL,
                    battery_capacity INTEGER NOT NULL,
                    state_of_charge INTEGER NOT NULL,
                    target_range_min INTEGER NOT NULL,
                    target_range_max INTEGER NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    out_of_service INTEGER DEFAULT 0,
                    mileage REAL DEFAULT 0.0,
                    last_maintenance_date TEXT,
                    in_service_date TEXT NOT NULL,
                    search_index TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_number INTEGER NOT NULL,
                    date_time TEXT NOT NULL,
                    username TEXT NOT NULL,
                    description TEXT NOT NULL,
                    additional_info TEXT,
                    suspicious INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            
            conn.commit()
            
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        raise


def create_user(username, password, first_name, last_name, role):
    try:
        from auth import hash_password

        password_hash = hash_password(password)
        
        username_hash = hashlib.sha256(username.lower().encode('utf-8')).hexdigest()

        encrypted_username = encrypt_data(username)
        encrypted_first_name = encrypt_data(first_name)
        encrypted_last_name = encrypt_data(last_name)
        encrypted_role = encrypt_data(role)
        
        registration_date = datetime.now().isoformat()
        encrypted_reg_date = encrypt_data(registration_date)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username_hash, username, password_hash, first_name, 
                                 last_name, role, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username_hash, encrypted_username, password_hash, encrypted_first_name,
                  encrypted_last_name, encrypted_role, encrypted_reg_date))
            conn.commit()
            
        log_event(
            username="system",
            description="New user account created",
            additional_info=f"Username: {username}, Role: {role}",
            suspicious=False
        )
        
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists")
    except Exception as e:
        raise Exception(f"Failed to create user: {str(e)}")


def get_user_by_username(username):
    try:
        username_hash = hashlib.sha256(username.lower().encode('utf-8')).hexdigest()
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username_hash = ?', (username_hash,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'username': decrypt_data(row['username']),
                    'password': row['password_hash'],
                    'first_name': decrypt_data(row['first_name']),
                    'last_name': decrypt_data(row['last_name']),
                    'role': decrypt_data(row['role']),
                    'registration_date': decrypt_data(row['registration_date'])
                }
            return None
            
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        return None


def update_user(username, **kwargs):
    try:
        username_hash = hashlib.sha256(username.lower().encode('utf-8')).hexdigest()
        
        valid_fields = ['first_name', 'last_name', 'role']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields and value is not None:
                updates.append(f"{field} = ?")
                values.append(encrypt_data(value))
        
        if not updates:
            return False
            
        values.append(username_hash)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            query = f"UPDATE users SET {', '.join(updates)} WHERE username_hash = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username=username,
                    description="User account updated",
                    additional_info=f"Fields: {', '.join(kwargs.keys())}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        return False


def delete_user(username):
    try:
        username_hash = hashlib.sha256(username.lower().encode('utf-8')).hexdigest()
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username_hash = ?', (username_hash,))
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username="system",
                    description="User account deleted",
                    additional_info=f"Username: {username}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        return False


def update_user_password(username, new_password):
    try:
        from auth import hash_password
        
        username_hash = hashlib.sha256(username.lower().encode('utf-8')).hexdigest()
        password_hash = hash_password(new_password)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE username_hash = ?',
                         (password_hash, username_hash))
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username=username,
                    description="Password updated",
                    additional_info="User password change",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error updating password: {str(e)}")
        return False


def get_all_users():
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY role, username')
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    'id': row['id'],
                    'username': decrypt_data(row['username']),
                    'first_name': decrypt_data(row['first_name']),
                    'last_name': decrypt_data(row['last_name']),
                    'role': decrypt_data(row['role']),
                    'registration_date': decrypt_data(row['registration_date'])
                })
            return users
            
    except Exception as e:
        print(f"Error retrieving users: {str(e)}")
        return []


def create_traveller(traveller_data):
    try:
        customer_id = generate_customer_id()
        
        encrypted_data = {}
        sensitive_fields = ['first_name', 'last_name', 'birthday', 'gender', 'street_name',
                          'house_number', 'zip_code', 'city', 'email', 'mobile_phone', 
                          'driving_license']
        
        for field in sensitive_fields:
            encrypted_data[field] = encrypt_data(traveller_data[field])
        
        # ervoor zorgen dat je nog wel kan zoeken
        search_index = f"{traveller_data['first_name']} {traveller_data['last_name']} " \
                      f"{traveller_data['email']} {customer_id}".lower()
        
        registration_date = datetime.now().isoformat()
        encrypted_reg_date = encrypt_data(registration_date)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO travellers (customer_id, first_name, last_name, birthday,
                                      gender, street_name, house_number, zip_code, city,
                                      email, mobile_phone, driving_license, registration_date,
                                      search_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, encrypted_data['first_name'], encrypted_data['last_name'],
                  encrypted_data['birthday'], encrypted_data['gender'], 
                  encrypted_data['street_name'], encrypted_data['house_number'],
                  encrypted_data['zip_code'], encrypted_data['city'], 
                  encrypted_data['email'], encrypted_data['mobile_phone'],
                  encrypted_data['driving_license'], encrypted_reg_date, search_index))
            conn.commit()
            
        log_event(
            username="system",
            description="New traveller registered",
            additional_info=f"Customer ID: {customer_id}",
            suspicious=False
        )
        
        return customer_id
        
    except Exception as e:
        raise Exception(f"Failed to create traveller: {str(e)}")


def search_travellers(search_term):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, customer_id, first_name, last_name, email
                FROM travellers 
                WHERE search_index LIKE ?
                ORDER BY customer_id
            ''', (f"%{search_term.lower()}%",))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'customer_id': row['customer_id'],
                    'first_name': decrypt_data(row['first_name']),
                    'last_name': decrypt_data(row['last_name']),
                    'email': decrypt_data(row['email'])
                })
            return results
            
    except Exception as e:
        print(f"Error searching travellers: {str(e)}")
        return []


def get_traveller_by_id(traveller_id):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM travellers WHERE id = ?', (traveller_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'customer_id': row['customer_id'],
                    'first_name': decrypt_data(row['first_name']),
                    'last_name': decrypt_data(row['last_name']),
                    'birthday': decrypt_data(row['birthday']),
                    'gender': decrypt_data(row['gender']),
                    'street_name': decrypt_data(row['street_name']),
                    'house_number': decrypt_data(row['house_number']),
                    'zip_code': decrypt_data(row['zip_code']),
                    'city': decrypt_data(row['city']),
                    'email': decrypt_data(row['email']),
                    'mobile_phone': decrypt_data(row['mobile_phone']),
                    'driving_license': decrypt_data(row['driving_license']),
                    'registration_date': decrypt_data(row['registration_date'])
                }
            return None
            
    except Exception as e:
        print(f"Error retrieving traveller: {str(e)}")
        return None


def update_traveller(traveller_id, **kwargs):
    try:
        valid_fields = ['first_name', 'last_name', 'birthday', 'gender', 'street_name',
                       'house_number', 'zip_code', 'city', 'email', 'mobile_phone',
                       'driving_license']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields and value is not None:
                updates.append(f"{field} = ?")
                values.append(encrypt_data(value))
        
        if not updates:
            return False
            
        #search index opnieuw updaten
        if any(field in ['first_name', 'last_name', 'email'] for field in kwargs.keys()):
            traveller = get_traveller_by_id(traveller_id)
            if traveller:
                new_search_index = f"{kwargs.get('first_name', traveller['first_name'])} " \
                                 f"{kwargs.get('last_name', traveller['last_name'])} " \
                                 f"{kwargs.get('email', traveller['email'])} " \
                                 f"{traveller['customer_id']}".lower()
                updates.append("search_index = ?")
                values.append(new_search_index)
        
        values.append(traveller_id)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            query = f"UPDATE travellers SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username="system",
                    description="Traveller data updated",
                    additional_info=f"Traveller ID: {traveller_id}, Fields: {', '.join(kwargs.keys())}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error updating traveller: {str(e)}")
        return False


def delete_traveller(traveller_id):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM travellers WHERE id = ?', (traveller_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username="system",
                    description="Traveller deleted",
                    additional_info=f"Traveller ID: {traveller_id}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error deleting traveller: {str(e)}")
        return False


def create_scooter(scooter_data):
    try:
        in_service_date = datetime.now().isoformat()
        
        search_index = f"{scooter_data['brand']} {scooter_data['model']} " \
                      f"{scooter_data['serial_number']}".lower()
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity,
                                    state_of_charge, target_range_min, target_range_max,
                                    latitude, longitude, out_of_service, mileage,
                                    last_maintenance_date, in_service_date, search_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (scooter_data['brand'], scooter_data['model'], scooter_data['serial_number'],
                  scooter_data['top_speed'], scooter_data['battery_capacity'], 
                  scooter_data['state_of_charge'], scooter_data['target_range_min'],
                  scooter_data['target_range_max'], scooter_data['latitude'], 
                  scooter_data['longitude'], scooter_data.get('out_of_service', 0),
                  scooter_data.get('mileage', 0.0), scooter_data.get('last_maintenance_date'),
                  in_service_date, search_index))
            conn.commit()
            
        log_event(
            username="system",
            description="New scooter added",
            additional_info=f"Serial: {scooter_data['serial_number']}",
            suspicious=False
        )
        
        return True
        
    except sqlite3.IntegrityError:
        raise ValueError("Serial number already exists")
    except Exception as e:
        raise Exception(f"Failed to create scooter: {str(e)}")


def search_scooters(search_term):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, brand, model, serial_number, state_of_charge, out_of_service
                FROM scooters 
                WHERE search_index LIKE ?
                ORDER BY brand, model
            ''', (f"%{search_term.lower()}%",))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'brand': row['brand'],
                    'model': row['model'],
                    'serial_number': row['serial_number'],
                    'state_of_charge': row['state_of_charge'],
                    'out_of_service': bool(row['out_of_service'])
                })
            return results
            
    except Exception as e:
        print(f"Error searching scooters: {str(e)}")
        return []


def get_scooter_by_id(scooter_id):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scooters WHERE id = ?', (scooter_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
    except Exception as e:
        print(f"Error retrieving scooter: {str(e)}")
        return None


def update_scooter(scooter_id, **kwargs):
    try:
        valid_fields = ['brand', 'model', 'serial_number', 'top_speed', 'battery_capacity',
                       'state_of_charge', 'target_range_min', 'target_range_max',
                       'latitude', 'longitude', 'out_of_service', 'mileage',
                       'last_maintenance_date']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields and value is not None:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
            
        if any(field in ['brand', 'model', 'serial_number'] for field in kwargs.keys()):
            scooter = get_scooter_by_id(scooter_id)
            if scooter:
                new_search_index = f"{kwargs.get('brand', scooter['brand'])} " \
                                 f"{kwargs.get('model', scooter['model'])} " \
                                 f"{kwargs.get('serial_number', scooter['serial_number'])}".lower()
                updates.append("search_index = ?")
                values.append(new_search_index)
        
        values.append(scooter_id)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            query = f"UPDATE scooters SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username="system",
                    description="Scooter data updated",
                    additional_info=f"Scooter ID: {scooter_id}, Fields: {', '.join(kwargs.keys())}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error updating scooter: {str(e)}")
        return False


def delete_scooter(scooter_id):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scooters WHERE id = ?', (scooter_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                log_event(
                    username="system",
                    description="Scooter deleted",
                    additional_info=f"Scooter ID: {scooter_id}",
                    suspicious=False
                )
                return True
            return False
            
    except Exception as e:
        print(f"Error deleting scooter: {str(e)}")
        return False


def log_event(username, description, additional_info="", suspicious=False):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(log_number) FROM system_logs')
            result = cursor.fetchone()
            log_number = (result[0] or 0) + 1
        
        encrypted_username = encrypt_data(username)
        encrypted_description = encrypt_data(description)
        encrypted_additional_info = encrypt_data(additional_info)
        
        date_time = datetime.now().isoformat()
        encrypted_date_time = encrypt_data(date_time)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (log_number, date_time, username, description,
                                       additional_info, suspicious)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (log_number, encrypted_date_time, encrypted_username, encrypted_description,
                  encrypted_additional_info, int(suspicious)))
            conn.commit()
            
        log_entry = {
            'log_number': log_number,
            'date_time': date_time,
            'username': username,
            'description': description,
            'additional_info': additional_info,
            'suspicious': suspicious
        }
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            encrypted_log = encrypt_log_data(log_entry)
            f.write(encrypted_log + '\n')
            
    except Exception as e:
        print(f"Error logging event: {str(e)}")


def get_logs(only_suspicious=False, limit=100):
    try:
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            
            if only_suspicious:
                cursor.execute('''
                    SELECT * FROM system_logs 
                    WHERE suspicious = 1 
                    ORDER BY log_number DESC 
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM system_logs 
                    ORDER BY log_number DESC 
                    LIMIT ?
                ''', (limit,))
                
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    'log_number': row['log_number'],
                    'date_time': decrypt_data(row['date_time']),
                    'username': decrypt_data(row['username']),
                    'description': decrypt_data(row['description']),
                    'additional_info': decrypt_data(row['additional_info']),
                    'suspicious': bool(row['suspicious'])
                })
            return logs
            
    except Exception as e:
        print(f"Error retrieving logs: {str(e)}")
        return []


def check_suspicious_logs_alert():
    try:
        suspicious_logs = get_logs(only_suspicious=True, limit=10)
        if suspicious_logs:
            print(f"\n⚠️  ALERT: {len(suspicious_logs)} suspicious activities detected!")
            print("Please review the system logs for security concerns.")
            
    except Exception as e:
        print(f"Error checking suspicious logs: {str(e)}")


def create_backup():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_FILE, "database.db")
            
            if os.path.exists(LOG_FILE):
                zipf.write(LOG_FILE, "system.log")
                
            metadata = {
                'backup_date': datetime.now().isoformat(),
                'version': '1.0',
                'description': 'Urban Mobility System Backup'
            }
            zipf.writestr("backup_info.json", json.dumps(metadata, indent=2))
        
        log_event(
            username="system",
            description="System backup created",
            additional_info=f"Backup file: {backup_filename}",
            suspicious=False
        )
        
        return backup_filename
        
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return None


def restore_backup(backup_filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError("Backup file not found")
        
        current_backup = create_backup()
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extract("database.db", ".")
            os.rename("database.db", DB_FILE)
            
            if "system.log" in zipf.namelist():
                zipf.extract("system.log", ".")
                os.rename("system.log", LOG_FILE)
        
        log_event(
            username="system", 
            description="System restored from backup",
            additional_info=f"Backup file: {backup_filename}, Current backup: {current_backup}",
            suspicious=False
        )
        
        return True
        
    except Exception as e:
        print(f"Error restoring backup: {str(e)}")
        return False


def list_backups():
    try:
        backups = []
        if os.path.exists(BACKUP_DIR):
            for filename in os.listdir(BACKUP_DIR):
                if filename.startswith("backup_") and filename.endswith(".zip"):
                    file_path = os.path.join(BACKUP_DIR, filename)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    backups.append({
                        'filename': filename,
                        'size': file_size,
                        'created': file_time.isoformat()
                    })
        return sorted(backups, key=lambda x: x['created'], reverse=True)
        
    except Exception as e:
        print(f"Error listing backups: {str(e)}")
        return []


def generate_restore_code_for_admin(admin_username, backup_filename):
    """Generate one-time restore code for specific admin and backup"""
    global restore_codes
    
    code = generate_restore_code()
    restore_codes[code] = {
        'admin_username': admin_username,
        'backup_file': backup_filename,
        'created': datetime.now().isoformat()
    }
    
    log_event(
        username="super_admin",
        description="Restore code generated",
        additional_info=f"Admin: {admin_username}, Backup: {backup_filename}",
        suspicious=False
    )
    
    return code


def use_restore_code(code, admin_username):
    """Use one-time restore code to perform backup restoration"""
    global restore_codes
    
    if code not in restore_codes:
        return False, "Invalid or expired restore code"
    
    code_data = restore_codes[code]
    if code_data['admin_username'] != admin_username:
        return False, "Restore code not issued for this administrator"
    
    backup_filename = code_data['backup_file']
    
    # Use the code (delete it)
    del restore_codes[code]
    
    # Perform restore
    success = restore_backup(backup_filename)
    
    log_event(
        username=admin_username,
        description="Backup restored using restore code",
        additional_info=f"Code: {code}, Backup: {backup_filename}, Success: {success}",
        suspicious=False
    )
    
    return success, "Restore completed successfully" if success else "Restore failed"


def revoke_restore_code(code):
    """Revoke a previously generated restore code"""
    global restore_codes
    
    if code in restore_codes:
        code_data = restore_codes[code]
        del restore_codes[code]
        
        log_event(
            username="super_admin",
            description="Restore code revoked",
            additional_info=f"Code: {code}, Admin: {code_data['admin_username']}",
            suspicious=False
        )
        return True
    return False


def list_restore_codes():
    """List active restore codes"""
    global restore_codes
    return [
        {
            'code': code,
            'admin_username': data['admin_username'],
            'backup_file': data['backup_file'],
            'created': data['created']
        }
        for code, data in restore_codes.items()
    ] 