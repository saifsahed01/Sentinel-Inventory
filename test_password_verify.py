"""
Test password verification against stored hash
"""
import bcrypt
import sqlite3

# Get the stored hash from database
conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()
cursor.execute('SELECT username, password_hash FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()
conn.close()

if user:
    username, stored_hash = user
    print(f"Testing password verification for user: {username}")
    print(f"Stored hash: {stored_hash[:60]}...")
    print()
    
    # Test common passwords
    test_passwords = [
        'admin123',
        'Admin123',
        'password',
        'admin',
        'Admin@123',
        '12345678'
    ]
    
    for password in test_passwords:
        try:
            result = bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )
            status = "[SUCCESS]" if result else "[FAILED]"
            print(f"{status} Password '{password}': {result}")
            
            if result:
                print(f"\n*** CORRECT PASSWORD FOUND: '{password}' ***\n")
        except Exception as e:
            print(f"[ERROR] Password '{password}': {e}")
else:
    print("User 'admin' not found in database")

# Made with Bob
