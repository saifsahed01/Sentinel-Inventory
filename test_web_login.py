import sys
sys.path.insert(0, 'src')

from data.database import DatabaseManager
from logic.auth import AuthenticationManager
from utils.config import Config
from utils.logger import AppLogger

print("=" * 70)
print("TESTING WEB APP LOGIN FLOW")
print("=" * 70)

# Initialize exactly as the web app does
config = Config(".env")
print(f"\n1. Config loaded from .env")
print(f"   Database path: {config.get_database_path()}")

db_manager = DatabaseManager(config.get_database_path())
print(f"\n2. DatabaseManager created")
print(f"   DB path: {db_manager.db_path}")

db_manager.connect()
print(f"\n3. Database connected")

auth_manager = AuthenticationManager(db_manager)
print(f"\n4. AuthenticationManager created")

# Test the login
username = 'admin'
password = 'password'

print(f"\n5. Attempting login...")
print(f"   Username: '{username}'")
print(f"   Password: '{password}'")

result = auth_manager.login(username, password)

print(f"\n6. Login result:")
if result:
    print(f"   SUCCESS!")
    print(f"   Session ID: {result['session_id']}")
    print(f"   Username: {result['username']}")
    print(f"   Role: {result['role']}")
else:
    print(f"   FAILED!")
    print(f"\n   Debugging:")
    
    # Check if user exists
    query = "SELECT username, password_hash, account_locked, failed_login_attempts FROM users WHERE username = ?"
    user_data = db_manager.fetch_one(query, (username,))
    
    if user_data:
        db_username, password_hash, locked, failed_attempts = user_data
        print(f"   - User found: {db_username}")
        print(f"   - Account locked: {locked}")
        print(f"   - Failed attempts: {failed_attempts}")
        print(f"   - Password hash: {password_hash[:30]}...")
        
        # Test password verification directly
        import bcrypt
        try:
            matches = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"   - Direct bcrypt check: {matches}")
        except Exception as e:
            print(f"   - Bcrypt error: {e}")
    else:
        print(f"   - User NOT found in database!")

print("\n" + "=" * 70)

# Made with Bob
