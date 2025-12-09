import json
from .data_loader import users, conversations, init_data
from local_chat.config.path import DATABASE_DIR

_ConnectionStatus = tuple[bool, str]  # (success, message)

class UserNotFoundException(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.msg = message
        self.code: int = code

def _save_database():
    """Save users and conversations back to the database file."""
    try:
        data = {
            "users": users,
            "conversations": conversations
        }
        with open(DATABASE_DIR, 'w') as json_file:
            json.dump(data, json_file, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}") #TODO: use rich print, fn in console_utils.py
        return False

def __login(phone_number: str, username: str, /) -> _ConnectionStatus:
    """
    Attempt to login with phone number and username.
    Returns (success, message) tuple.
    Raises UserNotFoundException if user doesn't exist.
    """
    phone_str = phone_number
    username_lower = username.strip().lower()
    
    # Find user by phone number
    user = next((u for u in users if u.get("number") == phone_str), None)
    
    if user is None:
        raise UserNotFoundException(f"User with phone number {phone_str} not found", 404)
    
    # Check if username matches (case-insensitive)
    if user.get("name", "").lower() != username_lower:
        return (False, "Username does not match the phone number")
    
    return (True, f"Welcome back, {user.get('name')}!")

def __sign_up(phone_number: str, username: str, /) -> _ConnectionStatus:
    """
    Create a new user account.
    Returns (success, message) tuple.
    """
    phone_str = phone_number
    username_clean = username.strip()
    
    #? for when i'll add seprate registration and login maybe
    existing_user = next((u for u in users if u.get("number") == phone_str), None)
    if existing_user:
        return (False, "Phone number already registered. Please login instead.")
    
    # Generate new user ID
    max_id = max([u.get("id", 0) for u in users], default=0)
    new_id = max_id + 1
    
    # Create new user
    new_user = {
        "id": new_id,
        "number": phone_str,
        "name": username_clean
    }
    
    users.append(new_user)
    
    if _save_database():
        # Reload data to ensure sync
        init_data()
        return (True, f"Account created successfully! Welcome, {username_clean}!")
    else:
        # Rollback if save failed
        users.pop()
        return (False, "Failed to save account. Please try again.")

def connect(phone_number: str, username: str) -> _ConnectionStatus:
    """
    Connect user by attempting login first, then sign up if user doesn't exist.
    Returns (success, message) tuple.
    """
    try:
        return __login(phone_number, username)
    except UserNotFoundException:
        return __sign_up(phone_number, username)

def get_user_id(phone_number: str, username: str) -> int | None:
    """
    Get user ID from database using phone number and username.
    Returns user ID if found and username matches, None otherwise.
    """
    phone_str = phone_number
    username_lower = username.strip().lower()
    
    # Find user by phone number
    user = next((u for u in users if u.get("number") == phone_str), None)
    
    if user is None:
        return None
    
    # Check if username matches (case-insensitive)
    if user.get("name", "").lower() != username_lower:
        return None
    
    return user.get("id")
    
if __name__ == "__main__":
    print(users)