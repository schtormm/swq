"""
Urban Mobility Backend System - Encryption Module
Symmetric encryption for sensitive data in database and logs
"""

import os
import base64
from cryptography.fernet import Fernet



# Global encryption object
_cipher = None
KEY_FILE = "um_encryption.key"


def initialize_encryption():
    """Initialize encryption system with key generation or loading"""
    global _cipher
    
    if os.path.exists(KEY_FILE):
        # Load existing key
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        # Generate new key
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


# Initialize encryption when module is imported
try:
    initialize_encryption()
except Exception:
    # Will be initialized when needed
    pass 