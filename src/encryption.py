#encryptie stuff
import base64
import os

from cryptography.fernet import Fernet

_cipher = None
KEY_FILE = "um_encryption.key"


def initialize_encryption():
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
    if _cipher is None:
        initialize_encryption()
    
    if data is None:
        return None
        
    assert isinstance(data, str), "Data must be a string"
    data_str = str(data)
    
    encrypted_bytes = _cipher.encrypt(data_str.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def decrypt_data(encrypted_data):
    if _cipher is None:
        initialize_encryption()
    
    if encrypted_data is None:
        return None
    
    try:
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_bytes = _cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # placeholder als er iets misgaat bij decrypt
        return f"[DECRYPTION_ERROR: {str(e)[:50]}...]"


def encrypt_log_data(log_data):
    if isinstance(log_data, dict):
        log_string = str(log_data)
    else:
        log_string = str(log_data)
    
    return encrypt_data(log_string)


def decrypt_log_data(encrypted_log_data):
    return decrypt_data(encrypted_log_data)

def is_encryption_initialized():
    return _cipher is not None and os.path.exists(KEY_FILE)


try:
    initialize_encryption()
except Exception:
    pass 