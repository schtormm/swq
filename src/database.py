#database access dingen
import hashlib
import json
import os
import sqlite3
import zipfile
from contextlib import closing
from datetime import datetime

from encryption import decrypt_data, encrypt_data, encrypt_log_data
from utils import generate_customer_id, generate_restore_code

# config zooi
DB_FILE = "urban_mobility.db"
LOG_FILE = "um_system.log"
BACKUP_DIR = "backups"

restore_codes = {}  # {code: {admin_username: str, backup_file: str, created: datetime}}


def get_db_connection():
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
                    additional_info=f"Username: {username} has been deleted",
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
        
        registration_date = datetime.now().isoformat()
        encrypted_reg_date = encrypt_data(registration_date)
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO travellers (customer_id, first_name, last_name, birthday,
                                      gender, street_name, house_number, zip_code, city,
                                      email, mobile_phone, driving_license, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, encrypted_data['first_name'], encrypted_data['last_name'],
                  encrypted_data['birthday'], encrypted_data['gender'], 
                  encrypted_data['street_name'], encrypted_data['house_number'],
                  encrypted_data['zip_code'], encrypted_data['city'], 
                  encrypted_data['email'], encrypted_data['mobile_phone'],
                  encrypted_data['driving_license'], encrypted_reg_date))
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
        search_lower = search_term.lower().strip()
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, customer_id, first_name, last_name, email
                FROM travellers 
                ORDER BY customer_id
            ''')
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                first_name = decrypt_data(row['first_name'])
                last_name = decrypt_data(row['last_name'])
                email = decrypt_data(row['email'])
                customer_id = row['customer_id']
                if (search_lower in first_name.lower() or 
                    search_lower in last_name.lower() or 
                    search_lower in email.lower() or 
                    search_lower in customer_id.lower() or
                    search_lower in f"{first_name} {last_name}".lower()):
                    
                    results.append({
                        'id': row['id'],
                        'customer_id': row['customer_id'],
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
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
        encrypted_in_service_date = encrypt_data(in_service_date)
        
        encrypted_data = {
            'brand': encrypt_data(scooter_data['brand']),
            'model': encrypt_data(scooter_data['model']),
            'serial_number': encrypt_data(scooter_data['serial_number']),
            'top_speed': encrypt_data(scooter_data['top_speed']),
            'battery_capacity': encrypt_data(scooter_data['battery_capacity']),
            'state_of_charge': encrypt_data(scooter_data['state_of_charge']),
            'target_range_min': encrypt_data(scooter_data['target_range_min']),
            'target_range_max': encrypt_data(scooter_data['target_range_max']),
            'latitude': encrypt_data(scooter_data['latitude']),
            'longitude': encrypt_data(scooter_data['longitude']),
            'mileage': encrypt_data(scooter_data.get('mileage', 0.0)),
            'last_maintenance_date': encrypt_data(scooter_data.get('last_maintenance_date', ''))
        }
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity,
                                    state_of_charge, target_range_min, target_range_max,
                                    latitude, longitude, out_of_service, mileage,
                                    last_maintenance_date, in_service_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (encrypted_data['brand'], encrypted_data['model'], encrypted_data['serial_number'],
                  encrypted_data['top_speed'], encrypted_data['battery_capacity'], 
                  encrypted_data['state_of_charge'], encrypted_data['target_range_min'],
                  encrypted_data['target_range_max'], encrypted_data['latitude'], 
                  encrypted_data['longitude'], scooter_data.get('out_of_service', 0),
                  encrypted_data['mileage'], encrypted_data['last_maintenance_date'],
                  encrypted_in_service_date))
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
        search_lower = search_term.lower().strip()
        
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, brand, model, serial_number, state_of_charge, out_of_service
                FROM scooters 
                ORDER BY brand, model
            ''')
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                brand = decrypt_data(row['brand'])
                model = decrypt_data(row['model'])
                serial_number = decrypt_data(row['serial_number'])
                if (search_lower in brand.lower() or 
                    search_lower in model.lower() or 
                    search_lower in serial_number.lower() or
                    search_lower in f"{brand} {model}".lower()):
                    
                    results.append({
                        'id': row['id'],
                        'brand': brand,
                        'model': model,
                        'serial_number': serial_number,
                        'state_of_charge': decrypt_data(row['state_of_charge']),
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
                return {
                    'id': row['id'],
                    'brand': decrypt_data(row['brand']),
                    'model': decrypt_data(row['model']), 
                    'serial_number': decrypt_data(row['serial_number']),
                    'top_speed': decrypt_data(row['top_speed']),
                    'battery_capacity': decrypt_data(row['battery_capacity']),
                    'state_of_charge': decrypt_data(row['state_of_charge']),
                    'target_range_min': decrypt_data(row['target_range_min']),
                    'target_range_max': decrypt_data(row['target_range_max']),
                    'latitude': decrypt_data(row['latitude']),
                    'longitude': decrypt_data(row['longitude']),
                    'out_of_service': bool(row['out_of_service']),
                    'mileage': decrypt_data(row['mileage']),
                    'last_maintenance_date': decrypt_data(row['last_maintenance_date']),
                    'in_service_date': decrypt_data(row['in_service_date'])
                }
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
                if field != 'out_of_service':
                    values.append(encrypt_data(value))
                else:
                    values.append(value)
 
                updates.append(f"{field} = ?")
                
        if not updates:
            return False
            
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
        log_event(
            username="system",
            description="Error updating scooter data",
            additional_info=f"Scooter ID: {scooter_id}, Error: {str(e)}",
            suspicious=True
        )
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
                  encrypted_additional_info, suspicious))
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
        
        # remove old database and log files
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extract("database.db", ".")
            os.rename("database.db", DB_FILE)
            
            if "system.log" in zipf.namelist():
                zipf.extract("system.log", ".")
                os.rename("system.log", LOG_FILE)
        
        log_event(
            username="system", 
            description="System restored from backup",
            additional_info=f"Backup file: {backup_filename}",
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
        log_event(
            username=admin_username,
            description="Attempted to use invalid restore code",
            additional_info=f"Code: {code}",
            suspicious=True
        )
        return False, "Invalid or expired restore code"
    
    
    code_data = restore_codes[code]
    if code_data['admin_username'] != admin_username:
        log_event(
            username=admin_username,
            description="Attempted to use restore code not issued for this admin",
            additional_info=f"Code: {code}, Expected Admin: {code_data['admin_username']}",
            suspicious=True
        )
        return False, "Restore code not issued for this administrator"
        
    
    backup_filename = code_data['backup_file']
    
    del restore_codes[code]
    
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