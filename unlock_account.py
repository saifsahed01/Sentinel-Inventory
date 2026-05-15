"""
Unlock Account Script
Resets account lockout status for a specified user.
"""
import sqlite3
import sys

def unlock_account(username, db_path="data/inventory.db"):
    """
    Unlock a user account by resetting failed login attempts and account_locked flag.
    
    Args:
        username: Username to unlock
        db_path: Path to the database file
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username, account_locked, failed_login_attempts FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"[X] User '{username}' not found in database.")
            conn.close()
            return False
        
        db_username, account_locked, failed_attempts = user
        print(f"\n[INFO] Current status for user '{db_username}':")
        print(f"   - Account Locked: {'Yes' if account_locked == 1 else 'No'}")
        print(f"   - Failed Login Attempts: {failed_attempts}")
        
        # Reset account lockout
        cursor.execute("""
            UPDATE users
            SET failed_login_attempts = 0,
                account_locked = 0
            WHERE username = ?
        """, (username,))
        
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT account_locked, failed_login_attempts FROM users WHERE username = ?", (username,))
        updated_user = cursor.fetchone()
        
        if updated_user:
            new_locked, new_attempts = updated_user
            print(f"\n[SUCCESS] Account unlocked successfully!")
            print(f"   - Account Locked: {'Yes' if new_locked == 1 else 'No'}")
            print(f"   - Failed Login Attempts: {new_attempts}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def list_locked_accounts(db_path="data/inventory.db"):
    """
    List all locked accounts in the database.
    
    Args:
        db_path: Path to the database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, failed_login_attempts, account_locked
            FROM users
            WHERE account_locked = 1 OR failed_login_attempts >= 5
        """)
        
        locked_users = cursor.fetchall()
        
        if not locked_users:
            print("\n[OK] No locked accounts found.")
        else:
            print(f"\n[LOCKED] Locked accounts ({len(locked_users)}):")
            for username, attempts, locked in locked_users:
                print(f"   - {username}: {attempts} failed attempts, locked={locked}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Account Unlock Utility")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        username = sys.argv[1]
        unlock_account(username)
    else:
        # List locked accounts first
        list_locked_accounts()
        
        # Prompt for username
        print("\nEnter username to unlock (or press Enter to exit):")
        username = input("> ").strip()
        
        if username:
            unlock_account(username)
        else:
            print("No username provided. Exiting.")
    
    print("\n" + "=" * 60)

# Made with Bob
