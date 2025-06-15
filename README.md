# Urban Mobility Backend System

A secure console-based backend system for managing Urban Mobility's shared electric scooter network in the Rotterdam region.

## System Overview

This system provides a secure backend interface for Urban Mobility employees to manage:
- **Travellers**: Customer accounts and information
- **Scooters**: Fleet management and monitoring
- **Users**: Backend system user accounts with role-based access
- **System Operations**: Logging, backup/restore, and security monitoring

## User Roles

### Super Administrator (Hard-coded)
- **Username**: `super_admin`
- **Password**: `Admin_123?`
- **Capabilities**: Full system access, can manage all user roles, generate restore codes

### System Administrator
- Can manage Service Engineers and Travellers
- Can add/update/delete scooters
- Can create backups and use restore codes
- Can view system logs

### Service Engineer
- Can update traveller accounts
- Can update limited scooter attributes (battery, location, maintenance)
- Cannot add/delete scooters or users

## Security Features

- **Encrypted Database**: All sensitive data encrypted with symmetric encryption
- **Password Hashing**: Secure bcrypt password hashing
- **Input Validation**: Comprehensive whitelisting-based validation
- **SQL Injection Protection**: Parameterized queries throughout
- **Activity Logging**: All actions logged with suspicious activity detection
- **Role-based Access Control**: Strict permission enforcement
- **Backup Security**: One-time restore codes for System Administrators

## Installation & Setup

1. **Install Python 3.8+**
   ```bash
   python3 --version  # Verify Python installation
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the System**
   ```bash
   python um_members.py
   ```

## First Time Setup

The system will automatically:
- Initialize the SQLite3 database
- Create encryption keys
- Set up the hard-coded Super Administrator account
- Create necessary directories (backups, logs)

## Usage Instructions

### Login
- Start the system with `python um_members.py`
- Use the Super Administrator credentials for initial access
- Create additional user accounts as needed

### Data Entry Formats

**Traveller Data:**
- Names: Letters, spaces, apostrophes, hyphens only
- Birthday: YYYY-MM-DD format
- Gender: male or female
- Zip Code: DDDDXX (4 digits + 2 uppercase letters)
- Mobile Phone: 8 digits only (system adds +31-6- prefix)
- Driving License: XXDDDDDDD or XDDDDDDDD format

**Scooter Data:**
- Serial Number: 10-17 alphanumeric characters
- GPS Coordinates: Rotterdam region (51.80000-52.10000, 4.20000-4.80000) with 5 decimal places
- Battery Percentage: 0-100
- Maintenance Date: YYYY-MM-DD format

**User Accounts:**
- Username: 8-10 characters, start with letter or underscore
- Password: 12-30 characters with uppercase, lowercase, digit, and special character

### Key Operations

**For Super Administrator:**
- Manage all user types
- Generate restore codes for System Administrators
- Full backup/restore capabilities
- Complete system oversight

**For System Administrator:**
- Manage Service Engineer accounts
- Handle traveller registration and updates
- Scooter fleet management
- System backup and restore (with codes)

**For Service Engineer:**
- Update traveller information
- Modify scooter status and location data
- Basic fleet monitoring

### Backup & Restore

**Creating Backups:**
- Available to Super Admin and System Admin
- Creates encrypted ZIP files in `backups/` directory
- Includes database and log files

**Restore Process:**
- Super Admin: Direct restore access
- System Admin: Requires one-time restore code from Super Admin
- Restores complete system state

### Security Monitoring

**System Logs:**
- All activities automatically logged
- Suspicious activities flagged (multiple failed logins, unauthorized access)
- Encrypted log storage
- Accessible to Super Admin and System Admin

**Data Protection:**
- Sensitive data encrypted in database
- Passwords never stored (only hashes)
- Secure key management
- Protection against common attacks

## File Structure

```
├── um_members.py           # Main entry point (required name)
├── um_main.py              # Application controller
├── um_auth.py              # Authentication & authorization
├── um_database.py          # Database operations
├── um_encryption.py        # Encryption services
├── um_validation.py        # Input validation
├── um_ui.py                # User interface menus
├── um_ui_operations.py     # Detailed UI operations
├── um_utils.py             # Utility functions
├── requirements.txt        # Python dependencies
├── README.md               # This documentation
├── urban_mobility.db       # SQLite database (auto-created)
├── um_system.log           # Encrypted system logs (auto-created)
├── um_encryption.key       # Encryption key (auto-created)
└── backups/                # Backup storage directory (auto-created)
```

## Technical Specifications

- **Database**: SQLite3 with encrypted sensitive data
- **Encryption**: Fernet symmetric encryption
- **Password Hashing**: bcrypt with salt
- **Input Validation**: Regex-based whitelisting
- **SQL Protection**: Parameterized queries
- **Logging**: Comprehensive encrypted activity logs
- **Python Version**: 3.8+
- **Dependencies**: bcrypt, cryptography

## Troubleshooting

**Common Issues:**

1. **Import Errors**: Ensure all required packages are installed
   ```bash
   pip install --upgrade bcrypt cryptography
   ```

2. **Database Locked**: Ensure no other instances are running

3. **Encryption Errors**: Delete `um_encryption.key` to regenerate (will lose encrypted data)

4. **Permission Errors**: Check file permissions in project directory

## Academic Notice

This system is designed for educational purposes as part of the Software Quality course assignment. The hard-coded Super Administrator credentials and some security approaches are intentionally simplified for assessment purposes and would not be appropriate for production use.

## Support

For technical issues or questions about system functionality, refer to the course materials or contact your instructor.