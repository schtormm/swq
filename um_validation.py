# validatie, met whitelisting deze keer!!!
import re
from datetime import date, datetime

from utils import get_cities_list, validate_latitude, validate_longitude

# whitelisting - wat mag er wel
# naam regex
NAME_PATTERN = r'^[A-Za-z\s\'\-]{1,50}$'

#username regex
USERNAME_PATTERN = r'^[A-Za-z_][A-Za-z0-9_\'\.]{7,9}$'

#email regex
EMAIL_PATTERN = r'^[a-zA-Z0-9\._%+-]+@[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,}$'

# 8 nummers voor telefoonnummer
PHONE_PATTERN = r'^[0-9]{8}$'

# postcode regex (dus 1234AB oid)
ZIP_CODE_PATTERN = r'^[0-9]{4}[A-Z]{2}$'

# regex voor rijbewijs
DRIVING_LICENSE_PATTERN = r'^[A-Z][0-9]{6,7}$'

# regex voor scooter serienummers
SERIAL_NUMBER_PATTERN = r'^[A-Za-z0-9]{10,17}$'

# alle dingen die in zoekopdracht mogen zitten
SEARCH_PATTERN = r'^[A-Za-z0-9\s\'\-\.@]{1,100}$'

ISO_DATUM_PATTERN = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'

# Percentage: 0-100 as whole numbers (including 0)
PERCENTAGE_PATTERN = r'^(100|[0-9]?[0-9])$'

# Positive integers: 1 or more digits, no leading zeros except single 0 (allow 0)
POSITIVE_INTEGER_PATTERN = r'^(0|[1-9][0-9]*)$'

# Positive floats: Numbers with optional decimal places, no leading zeros, no trailing decimal
POSITIVE_FLOAT_PATTERN = r'^(0|[1-9][0-9]*)(\.[0-9]+)?$'

GPS_COORDINATE_PATTERN = r'^[0-9]+\.[0-9]{5}$'

# regexes voor in wachtwoord
PASSWORD_ALLOWED_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%&_-+=`|\\(){}[]:;\'<>,.?/')
PASSWORD_LOWERCASE = set('abcdefghijklmnopqrstuvwxyz')
PASSWORD_UPPERCASE = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
PASSWORD_DIGITS = set('0123456789')
PASSWORD_SPECIAL = set('~!@#$%&_-+=`|\\(){}[]:;\'<>,.?/')

ALLOWED_GENDERS = {"male", "female"} 

def is_safe_string(input_str):
    return input_str is not None and '\x00' not in str(input_str)


def is_valid_length(input_str, min_length=None, max_length=None):
    if input_str is None:
        return min_length is None or min_length == 0
    
    length = len(str(input_str))
    min_ok = min_length is None or length >= min_length
    max_ok = max_length is None or length <= max_length
    return min_ok and max_ok


def matches_whitelist_pattern(input_str, pattern):
    return (input_str and 
            isinstance(input_str, str) and 
            is_safe_string(input_str) and 
            re.fullmatch(pattern, input_str) is not None)


def validate_username(username):
    if (username and 
        isinstance(username, str) and 
        is_safe_string(username) and 
        is_valid_length(username, 8, 10) and 
        re.fullmatch(USERNAME_PATTERN, username.lower())):  # Case-insensitive validation
        return True, ""
    else:
        return False, "Username must be 8-10 characters, start with letter/underscore, contain only letters, numbers, underscores, apostrophes, periods (case-insensitive)"


def validate_password(password):
    if (password and 
        isinstance(password, str) and 
        is_safe_string(password) and 
        is_valid_length(password, 12, 30) and 
        all(c in PASSWORD_ALLOWED_CHARS for c in password) and
        any(c in PASSWORD_LOWERCASE for c in password) and
        any(c in PASSWORD_UPPERCASE for c in password) and
        any(c in PASSWORD_DIGITS for c in password) and
        any(c in PASSWORD_SPECIAL for c in password)):
        return True, ""
    else:
        return False, "Password must be 12-30 characters with lowercase, uppercase, digit, and special character from allowed set"


def validate_name(name, field_name="Name"):
    if (name and 
        isinstance(name, str) and 
        is_safe_string(name) and 
        is_valid_length(name, 1, 50) and 
        re.fullmatch(NAME_PATTERN, name)):
        return True, ""
    else:
        return False, f"{field_name} must be 1-50 characters containing only letters, spaces, apostrophes, hyphens"


def validate_email(email):
    if (email and 
        isinstance(email, str) and 
        is_safe_string(email) and 
        is_valid_length(email, 5, 100) and 
        re.fullmatch(EMAIL_PATTERN, email)):
        return True, ""
    else:
        return False, "Email must be 5-100 characters in valid format with allowed characters only"


def validate_mobile_phone(phone):
    if (phone and 
        isinstance(phone, str) and 
        is_safe_string(phone) and 
        re.fullmatch(PHONE_PATTERN, phone)):
        return True, ""
    else:
        return False, "Mobile phone must be exactly 8 digits"


def validate_zip_code(zip_code):
    if (zip_code and 
        isinstance(zip_code, str) and 
        is_safe_string(zip_code) and 
        re.fullmatch(ZIP_CODE_PATTERN, zip_code)):
        return True, ""
    else:
        return False, "Zip code must be exactly DDDDXX format (4 digits + 2 uppercase letters)"


def validate_city(city):
    allowed_cities = set(get_cities_list())
    if (city and 
        isinstance(city, str) and 
        is_safe_string(city) and 
        city in allowed_cities):
        return True, ""
    else:
        return False, f"City must be one of: {', '.join(sorted(allowed_cities))}"


def validate_gender(gender):
    if (gender and 
        isinstance(gender, str) and 
        is_safe_string(gender) and 
        gender.lower() in ALLOWED_GENDERS):
        return True, ""
    else:
        return False, f"Gender must be one of: {', '.join(ALLOWED_GENDERS)}"


def validate_date(date_str, field_name="Date"):
    if (date_str and 
        isinstance(date_str, str) and 
        is_safe_string(date_str) and 
        re.fullmatch(ISO_DATUM_PATTERN, date_str)):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, f"Invalid {field_name.lower()} - not a valid calendar date"
    else:
        return False, f"{field_name} must be in YYYY-MM-DD format"


def validate_driving_license(license_num):
    if (license_num and 
        isinstance(license_num, str) and 
        is_safe_string(license_num) and 
        re.fullmatch(DRIVING_LICENSE_PATTERN, license_num)):
        return True, ""
    else:
        return False, "Driving license must be 1 letter followed by 6-7 digits"


def validate_scooter_serial(serial):
    if (serial and 
        isinstance(serial, str) and 
        is_safe_string(serial) and 
        re.fullmatch(SERIAL_NUMBER_PATTERN, serial)):
        return True, ""
    else:
        return False, "Serial number must be 10-17 alphanumeric characters"


def validate_positive_integer(value, field_name="Value", min_val=None, max_val=None):
    if (value and 
        isinstance(value, str) and 
        is_safe_string(value) and 
        re.fullmatch(POSITIVE_INTEGER_PATTERN, value)):
        try:
            int_val = int(value)
            min_ok = min_val is None or int_val >= min_val
            max_ok = max_val is None or int_val <= max_val
            if min_ok and max_ok:
                return True, ""
            else:
                return False, f"{field_name} must be between {min_val or 1} and {max_val or 'unlimited'}"
        except ValueError:
            return False, f"{field_name} must be a valid positive integer"
    else:
        return False, f"{field_name} must be a positive integer without leading zeros"


def validate_positive_float(value, field_name="Value", min_val=None, max_val=None):
    if (value and 
        isinstance(value, str) and 
        is_safe_string(value) and 
        re.fullmatch(POSITIVE_FLOAT_PATTERN, value)):
        try:
            float_val = float(value)
            min_ok = min_val is None or float_val >= min_val
            max_ok = max_val is None or float_val <= max_val
            if min_ok and max_ok:
                return True, ""
            else:
                return False, f"{field_name} must be between {min_val or 0} and {max_val or 'unlimited'}"
        except ValueError:
            return False, f"{field_name} must be a valid positive number"
    else:
        return False, f"{field_name} must be a positive number"


def validate_percentage(value, field_name="Percentage"):
    if (value and 
        isinstance(value, str) and 
        is_safe_string(value) and 
        re.fullmatch(PERCENTAGE_PATTERN, value)):
        return True, ""
    else:
        return False, f"{field_name} must be a whole number between 0 and 100"


def validate_gps_coordinates(latitude, longitude):
    lat_valid = (latitude and 
                isinstance(latitude, str) and 
                is_safe_string(latitude) and 
                re.fullmatch(GPS_COORDINATE_PATTERN, latitude) and 
                validate_latitude(latitude))
    
    lng_valid = (longitude and 
                isinstance(longitude, str) and 
                is_safe_string(longitude) and 
                re.fullmatch(GPS_COORDINATE_PATTERN, longitude) and 
                validate_longitude(longitude))
    
    if lat_valid and lng_valid:
        return True, ""
    else:
        return False, "GPS coordinates must be in Rotterdam region with exactly 5 decimal places (lat: 51.80000-52.10000, lng: 4.20000-4.80000)"


def validate_search_term(search_term):
    if (search_term and 
        isinstance(search_term, str) and 
        is_safe_string(search_term) and 
        is_valid_length(search_term, 1, 100) and 
        re.fullmatch(SEARCH_PATTERN, search_term)):
        return True, ""
    else:
        return False, "Search term must be 1-100 characters containing only letters, numbers, spaces, apostrophes, hyphens, dots, @ symbols"


def get_validated_input(prompt, validation_func, *args, **kwargs):
    while True:
        try:
            user_input = input(prompt).strip()
            is_valid, error_msg = validation_func(user_input, *args, **kwargs)
            
            if is_valid:
                return user_input
            else:
                print(f"{error_msg}")
                
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Input validation error: {str(e)}")


def validate_choice(choice, valid_choices):
    allowed_choices = set(valid_choices)
    if (choice and 
        isinstance(choice, str) and 
        is_safe_string(choice) and 
        choice in allowed_choices):
        return True, ""
    else:
        return False, f"Choice must be one of: {', '.join(valid_choices)}" 