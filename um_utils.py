"""
Urban Mobility Backend System - Utility Functions
Common utility functions used throughout the system
"""

import random
import string
from datetime import datetime


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60)


def print_separator():
    """Print separator line"""
    print("-" * 60)


def print_sub_header(title):
    """Print formatted sub-header"""  
    print(f"\n--- {title} ---")


def generate_customer_id():
    """Generate unique customer ID for travellers"""
    # Generate 10-digit unique ID
    return str(random.randint(1000000000, 9999999999))


def format_datetime(dt_string):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string


def generate_temp_password():
    """Generate temporary password for reset operations"""
    # Generate 12-character temporary password meeting requirements
    chars = string.ascii_letters + string.digits + "!@#$%&"
    password = (
        random.choice(string.ascii_lowercase) +  # at least one lowercase
        random.choice(string.ascii_uppercase) +  # at least one uppercase  
        random.choice(string.digits) +           # at least one digit
        random.choice("!@#$%&") +               # at least one special char
        ''.join(random.choices(chars, k=8))      # fill to 12 chars
    )
    # Shuffle to randomize positions
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_restore_code():
    """Generate one-time restore code for backup restoration"""
    # Generate 16-character alphanumeric code
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=16))


def validate_latitude(lat_str):
    """Validate Rotterdam region latitude (5 decimal places)"""
    try:
        lat = float(lat_str)
        # Rotterdam region approximately 51.8 to 52.1
        if 51.80000 <= lat <= 52.10000:
            # Check 5 decimal places
            if len(lat_str.split('.')[-1]) == 5:
                return True
    except:
        pass
    return False


def validate_longitude(lng_str):
    """Validate Rotterdam region longitude (5 decimal places)"""
    try:
        lng = float(lng_str)
        # Rotterdam region approximately 4.2 to 4.8
        if 4.20000 <= lng <= 4.80000:
            # Check 5 decimal places  
            if len(lng_str.split('.')[-1]) == 5:
                return True
    except:
        pass
    return False


def format_location(latitude, longitude):
    """Format GPS coordinates for display"""
    return f"{latitude:.5f}, {longitude:.5f}"


def create_display_table(headers, rows):
    """Create formatted table for console display"""
    if not rows:
        return "No data to display"
        
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in rows:
            if i < len(row) and row[i] is not None:
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width + 2, 30))  # Max width 30 chars
    
    # Create header
    result = []
    header_line = "|".join(f"{headers[i]:^{col_widths[i]}}" for i in range(len(headers)))
    result.append(header_line)
    result.append("-" * len(header_line))
    
    # Add rows
    for row in rows:
        row_line = "|".join(
            f"{str(row[i]) if i < len(row) and row[i] is not None else '':^{col_widths[i]}}" 
            for i in range(len(headers))
        )
        result.append(row_line)
    
    return "\n".join(result)


def truncate_text(text, max_length=50):
    """Truncate text with ellipsis if too long"""
    if text is None:
        return ""
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length-3] + "..."


def format_search_results(results, result_type="items"):
    """Format search results for display"""
    if not results:
        return f"No {result_type} found matching your search criteria."
    
    count = len(results)
    return f"Found {count} {result_type}{'s' if count != 1 else ''} matching your search:"


def get_cities_list():
    """Get predefined list of 10 cities"""
    return [
        "Rotterdam", "Amsterdam", "Utrecht", "The Hague", "Eindhoven",
        "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"
    ] 