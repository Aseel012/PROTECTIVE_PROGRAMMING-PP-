"""
Level 2: Validation & Sanitization - Production Style
Username/Email/Age validation with whitelisting, blacklisting, regex, and boundary cases
Interactive user input version with JSON storage
"""

import re
import logging
import json
import os
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Standardized validation result container"""
    is_valid: bool
    data: Optional[Dict[str, Any]] = None
    errors: Dict[str, str] = field(default_factory=dict)
    sanitized_data: Optional[Dict[str, Any]] = None
    
    def __bool__(self):
        return self.is_valid
    
    def add_error(self, field: str, message: str):
        self.errors[field] = message
        self.is_valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'valid': self.is_valid,
            'data': self.sanitized_data or self.data,
            'errors': self.errors
        }


@dataclass
class UserRecord:
    """User record for storage"""
    username: str
    email: str
    age: int
    validated_at: str
    validation_status: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UserDataStorage:
    """Handle storage of validated user data in JSON"""
    
    def __init__(self, storage_file: str = "validated_users.json"):
        self.storage_file = storage_file
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Create storage file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Save validated user data to JSON file
        
        Args:
            user_data: Sanitized user data (username, email, age)
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing data
            with open(self.storage_file, 'r') as f:
                users = json.load(f)
            
            # Create user record with timestamp
            record = UserRecord(
                username=user_data['username'],
                email=user_data['email'],
                age=user_data['age'],
                validated_at=datetime.now().isoformat(),
                validation_status='PASSED'
            )
            
            # Add to list and save
            users.append(record.to_dict())
            
            with open(self.storage_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"User {user_data['username']} saved to storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user data: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieve all stored users"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return []
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user by username"""
        users = self.get_all_users()
        for user in users:
            if user['username'].lower() == username.lower():
                return user
        return None
    
    def delete_user(self, username: str) -> bool:
        """Delete a user by username"""
        try:
            users = self.get_all_users()
            users = [u for u in users if u['username'].lower() != username.lower()]
            
            with open(self.storage_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            logger.info(f"User {username} deleted from storage")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        users = self.get_all_users()
        return {
            'total_users': len(users),
            'latest_validation': users[-1]['validated_at'] if users else None,
            'usernames': [u['username'] for u in users]
        }


class UserInputValidator:
    """
    Production-grade validator with:
    - Whitelisting (allowed patterns)
    - Blacklisting (prohibited patterns)
    - Regex pattern matching
    - Boundary case handling
    - Fail-safe error responses
    """
    
    USERNAME_WHITELIST = re.compile(r'^[a-zA-Z0-9._]{3,30}$')
    
    USERNAME_BLACKLIST = {
        'admin', 'root', 'system', 'superuser', 'moderator', 
        'administrator', 'support', 'helpdesk', 'test', 'guest'
    }
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    EMAIL_BLACKLIST_DOMAINS = {
        'tempmail.com', 'guerrillamail.com', 'throwaway.com',
        'temp-mail.org', 'mailinator.com', '10minutemail.com'
    }
    
    AGE_MIN = 13
    AGE_MAX = 120
    
    BOUNDARY_CASES = {
        'age': {
            'min': AGE_MIN,
            'max': AGE_MAX,
            'edge_values': [AGE_MIN - 1, AGE_MIN, AGE_MIN + 1, AGE_MAX - 1, AGE_MAX, AGE_MAX + 1],
            'special': ['0', '-1', '999', 'abc', None, '', '13.5']
        },
        'username': {
            'min_length': 3,
            'max_length': 30,
            'edge_cases': ['a', 'ab', 'abc', 'a'*30, 'a'*31, 'user@name', 'user name']
        }
    }
    
    def __init__(self):
        self._validation_stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0
        }
        self.storage = UserDataStorage()
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate username with whitelist, blacklist, and boundary checks"""
        if not username:
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        if len(username) < self.BOUNDARY_CASES['username']['min_length']:
            return False, f"Username must be at least {self.BOUNDARY_CASES['username']['min_length']} characters"
        
        if len(username) > self.BOUNDARY_CASES['username']['max_length']:
            return False, f"Username cannot exceed {self.BOUNDARY_CASES['username']['max_length']} characters"
        
        if not self.USERNAME_WHITELIST.match(username):
            return False, "Username can only contain letters, numbers, dots, and underscores"
        
        if username.lower() in self.USERNAME_BLACKLIST:
            return False, f"Username '{username}' is not available"
        
        if '..' in username or '__' in username:
            return False, "Username cannot contain consecutive dots or underscores"
        
        if username.startswith(('.', '_')):
            return False, "Username cannot start with dot or underscore"
        if username.endswith(('.', '_')):
            return False, "Username cannot end with dot or underscore"
        
        # Check if username already exists in storage
        existing_user = self.storage.get_user_by_username(username)
        if existing_user:
            return False, f"Username '{username}' is already taken"
        
        return True, ""
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email with regex, whitelist domains, and boundary checks"""
        if not email:
            return False, "Email cannot be empty"
        
        email = email.strip().lower()
        
        if not self.EMAIL_PATTERN.match(email):
            return False, "Please enter a valid email address"
        
        try:
            _, domain = email.split('@', 1)
        except ValueError:
            return False, "Invalid email format"
        
        if domain in self.EMAIL_BLACKLIST_DOMAINS:
            return False, "Email provider is not allowed. Please use a permanent email address"
        
        if len(email) > 254:
            return False, "Email address is too long"
        
        local_part = email.split('@')[0]
        if len(local_part) > 64:
            return False, "Email local part is too long"
        
        if '..' in email:
            return False, "Email cannot contain consecutive dots"
        
        return True, ""
    
    def validate_age(self, age_input: Any) -> Tuple[bool, str]:
        """Validate age with comprehensive boundary testing"""
        if age_input is None or age_input == '':
            return False, "Age is required"
        
        try:
            age = int(age_input)
        except (ValueError, TypeError):
            return False, "Age must be a valid number"
        
        if age < 0:
            return False, "Age cannot be negative"
        
        if age > self.AGE_MAX * 10:
            return False, "Invalid age value"
        
        if age < self.AGE_MIN:
            return False, f"You must be at least {self.AGE_MIN} years old"
        
        if age > self.AGE_MAX:
            return False, f"Age cannot exceed {self.AGE_MAX} years"
        
        return True, ""
    
    def validate_all(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate all fields and return comprehensive result"""
        self._validation_stats['total_validations'] += 1
        
        result = ValidationResult(is_valid=True, data=data.copy())
        sanitized = {}
        
        username = data.get('username')
        is_valid, error = self.validate_username(username)
        if not is_valid:
            result.add_error('username', error)
        else:
            sanitized['username'] = username.strip()
        
        email = data.get('email')
        is_valid, error = self.validate_email(email)
        if not is_valid:
            result.add_error('email', error)
        else:
            sanitized['email'] = email.strip().lower()
        
        age = data.get('age')
        is_valid, error = self.validate_age(age)
        if not is_valid:
            result.add_error('age', error)
        else:
            sanitized['age'] = int(age)
        
        if result.is_valid:
            self._validation_stats['passed'] += 1
            result.sanitized_data = sanitized
            logger.info(f"Validation PASSED for user: {sanitized.get('username')}")
            
            # Save to JSON storage
            if self.storage.save_user(sanitized):
                logger.info(f"User data saved to {self.storage.storage_file}")
        else:
            self._validation_stats['failed'] += 1
            logger.warning(f"Validation FAILED: {result.errors}")
        
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """Get validation statistics"""
        return self._validation_stats.copy()


def get_user_input(prompt: str, field_type: str = 'text') -> str:
    """Get user input with basic sanitization"""
    while True:
        user_input = input(prompt)
        if field_type == 'age':
            return user_input
        if user_input.strip():
            return user_input
        print("  Input cannot be empty. Please try again.")


def view_stored_users(storage: UserDataStorage):
    """Display all stored users"""
    users = storage.get_all_users()
    if not users:
        print("\nNo users found in storage.")
        return
    
    print("\n" + "=" * 60)
    print("STORED USERS")
    print("=" * 60)
    print(f"Total users: {len(users)}")
    print("-" * 60)
    
    for idx, user in enumerate(users, 1):
        print(f"{idx}. Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Age: {user['age']}")
        print(f"   Validated: {user['validated_at']}")
        print(f"   Status: {user['validation_status']}")
        print("-" * 60)


def main():
    """Main interactive validation program with storage"""
    validator = UserInputValidator()
    storage = UserDataStorage()
    
    print("=" * 60)
    print("USER VALIDATION SYSTEM WITH JSON STORAGE")
    print("=" * 60)
    
    while True:
        print("\n" + "-" * 60)
        print("MAIN MENU")
        print("-" * 60)
        print("1. Register new user")
        print("2. View all stored users")
        print("3. Search for a user")
        print("4. Delete a user")
        print("5. View storage statistics")
        print("6. Exit")
        print("-" * 60)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            # Register new user
            attempts = 0
            max_attempts = 3
            
            while attempts < max_attempts:
                print(f"\n--- Registration Attempt {attempts + 1} of {max_attempts} ---")
                print("(Enter 'quit' to return to main menu)")
                
                username = get_user_input("Enter username (3-30 chars, alphanumeric, ._): ")
                if username.lower() == 'quit':
                    break
                
                email = get_user_input("Enter email address: ")
                if email.lower() == 'quit':
                    break
                
                age_input = get_user_input("Enter age (13-120): ", 'age')
                if age_input.lower() == 'quit':
                    break
                
                user_data = {
                    'username': username,
                    'email': email,
                    'age': age_input
                }
                
                result = validator.validate_all(user_data)
                
                if result:
                    print("\n" + "=" * 60)
                    print("REGISTRATION SUCCESSFUL")
                    print("=" * 60)
                    print(f"Username: {result.sanitized_data['username']}")
                    print(f"Email: {result.sanitized_data['email']}")
                    print(f"Age: {result.sanitized_data['age']}")
                    print(f"\nData saved to: {storage.storage_file}")
                    break
                else:
                    print("\n" + "-" * 60)
                    print("REGISTRATION FAILED")
                    print("-" * 60)
                    for field, error in result.errors.items():
                        print(f"  • {field.capitalize()}: {error}")
                    
                    attempts += 1
                    if attempts >= max_attempts:
                        print("\nMaximum registration attempts reached.")
        
        elif choice == '2':
            view_stored_users(storage)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            # Search for a user
            username = input("Enter username to search: ").strip()
            if username:
                user = storage.get_user_by_username(username)
                if user:
                    print("\n" + "=" * 60)
                    print("USER FOUND")
                    print("=" * 60)
                    print(f"Username: {user['username']}")
                    print(f"Email: {user['email']}")
                    print(f"Age: {user['age']}")
                    print(f"Validated: {user['validated_at']}")
                    print(f"Status: {user['validation_status']}")
                else:
                    print(f"\nNo user found with username '{username}'")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            # Delete a user
            username = input("Enter username to delete: ").strip()
            if username:
                confirm = input(f"Are you sure you want to delete '{username}'? (y/n): ")
                if confirm.lower() == 'y':
                    if storage.delete_user(username):
                        print(f"User '{username}' deleted successfully.")
                    else:
                        print(f"Failed to delete user '{username}'.")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            # View statistics
            stats = storage.get_statistics()
            print("\n" + "=" * 60)
            print("STORAGE STATISTICS")
            print("=" * 60)
            print(f"Total registered users: {stats['total_users']}")
            if stats['latest_validation']:
                print(f"Latest registration: {stats['latest_validation']}")
            print(f"Usernames: {', '.join(stats['usernames']) if stats['usernames'] else 'None'}")
            
            # Validation statistics
            val_stats = validator.get_stats()
            print(f"\nValidation Statistics:")
            print(f"  Total validations: {val_stats['total_validations']}")
            print(f"  Successful: {val_stats['passed']}")
            print(f"  Failed: {val_stats['failed']}")
            if val_stats['total_validations'] > 0:
                pass_rate = (val_stats['passed'] / val_stats['total_validations']) * 100
                print(f"  Pass rate: {pass_rate:.1f}%")
            
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            print("\nThank you for using the validation system!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()