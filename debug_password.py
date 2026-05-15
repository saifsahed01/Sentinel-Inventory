import sqlite3
import bcrypt

# Get the stored hash from database
conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()
cursor.execute('SELECT username, password_hash FROM users WHERE username = ?', ('admin',))
result = cursor.fetchone()
conn.close()

if result:
    username, stored_hash = result
    print(f"Username: {username}")
    print(f"Stored hash: {stored_hash}")
    print(f"Hash type: {type(stored_hash)}")
    print(f"Hash length: {len(stored_hash)}")
    print()
    
    # Test with the password we think is correct
    test_password = 'password'
    print(f"Testing password: '{test_password}'")
    print()
    
    # Try verification
    try:
        result = bcrypt.checkpw(
            test_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
        print(f"bcrypt.checkpw result: {result}")
    except Exception as e:
        print(f"Error during verification: {e}")
        print(f"Error type: {type(e)}")
else:
    print("User not found!")

# Made with Bob
