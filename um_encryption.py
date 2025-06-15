"""
Urban Mobility Backend System - Encryption Module
Symmetric encryption for sensitive data in database and logs
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Global encryption object
_cipher = None
KEY_FILE = "um_encryption.key"


def initialize_encryption():
    """Initialize encryption system with key generation or loading"""
    global _cipher
    
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    
    _cipher = Fernet(key)


def encrypt_data(data):
    """
    Encrypt sensitive data using symmetric encryption
    Args:
        data: String data to encrypt
    Returns:
        Encrypted data as base64 encoded string for database storage
    """
    if _cipher is None:
        initialize_encryption()
    
    if data is None:
        return None
        
    # Convert to string if not already
    data_str = str(data)
    
    # Encrypt and encode to base64 for database storage
    encrypted_bytes = _cipher.encrypt(data_str.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def decrypt_data(encrypted_data):
    """
    Decrypt data that was encrypted with encrypt_data
    Args:
        encrypted_data: Base64 encoded encrypted string from database
    Returns:
        Original decrypted string
    """
    if _cipher is None:
        initialize_encryption()
    
    if encrypted_data is None:
        return None
    
    try:
        # Decode from base64 and decrypt
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_bytes = _cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # Return placeholder for corrupted data
        return f"[DECRYPTION_ERROR: {str(e)[:50]}...]"


def encrypt_log_data(log_data):
    """
    Encrypt log data for secure log file storage
    Args:
        log_data: Dictionary or string containing log information
    Returns:
        Encrypted log data as base64 string
    """
    if isinstance(log_data, dict):
        # Convert dict to string representation
        log_string = str(log_data)
    else:
        log_string = str(log_data)
    
    return encrypt_data(log_string)


def decrypt_log_data(encrypted_log_data):
    """
    Decrypt log data from secure log file
    Args:
        encrypted_log_data: Base64 encrypted string
    Returns:
        Decrypted log data as string
    """
    return decrypt_data(encrypted_log_data)


def secure_delete_key():
    """
    Securely delete encryption key (for system reset scenarios)
    WARNING: This will make all encrypted data unrecoverable!
    """
    global _cipher
    _cipher = None
    
    if os.path.exists(KEY_FILE):
        # Overwrite file with random data before deletion
        file_size = os.path.getsize(KEY_FILE)
        with open(KEY_FILE, 'rb+') as f:
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())
        
        os.remove(KEY_FILE)


def is_encryption_initialized():
    """Check if encryption system is properly initialized"""
    return _cipher is not None and os.path.exists(KEY_FILE)


# Initialize encryption when module is imported
try:
    initialize_encryption()
except Exception:
    # Will be initialized when needed
    pass 