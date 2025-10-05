
#utils voor gebruik in rest v/h systeem
import random
import string
from datetime import datetime


# fancy print functions
def print_header(title):
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60)


def print_separator():
    print("-" * 60)


def print_sub_header(title):
    print(f"\n--- {title} ---")


# rest v/d utils
def generate_customer_id():
    return str(random.randint(1000000000, 9999999999))


def format_datetime(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string


def generate_temp_password():
    chars = string.ascii_letters + string.digits + "!@#$%&"
    password = (
        random.choice(string.ascii_lowercase) +  # tenminste 1 lowercase
        random.choice(string.ascii_uppercase) +  # tenminste 1 uppercase  
        random.choice(string.digits) +           # tenminste 1 nummer
        random.choice("!@#$%&") +               # tenminste 1 speciaal karakter
        ''.join(random.choices(chars, k=8))      # en afmaken tot 12 karakters
    )
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)


def generate_restore_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=16))




def format_location(latitude, longitude):
    return f"{latitude:.5f}, {longitude:.5f}"


def create_display_table(headers, rows):
    if not rows:
        return "No data to display"
        
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in rows:
            if i < len(row) and row[i] is not None:
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width + 2, 30)) #karakter limiet = 30
    
    result = []
    header_line = "|".join(f"{headers[i]:^{col_widths[i]}}" for i in range(len(headers)))
    result.append(header_line)
    result.append("-" * len(header_line))
    
    for row in rows:
        row_line = "|".join(
            f"{str(row[i]) if i < len(row) and row[i] is not None else '':^{col_widths[i]}}" 
            for i in range(len(headers))
        )
        result.append(row_line)
    
    return "\n".join(result)


def truncate_text(text, max_length=50):
    if text is None:
        return ""
    text_str = str(text)
    if len(text_str) <= max_length:
        return text_str
    return text_str[:max_length-3] + "..."

def get_cities_list():
    return [
        "Rotterdam", "Amsterdam", "Utrecht", "The Hague", "Eindhoven",
        "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"
    ] 