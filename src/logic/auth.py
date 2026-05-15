"""
Authentication Manager Module
Handles user authentication with bcrypt password hashing and session management.
"""
import bcrypt
import secrets
import time
from typing import Optional, Dict
from datetime import datetime, timedelta


class AuthenticationManager:
    """
    Manages user authentication, password hashing, and session management.
    Implements security features like account lockout and session timeout.
    """
    
    # Security constants
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT_MINUTES = 30
    BCRYPT_ROUNDS = 12
    
    def __init__(self, db_manager):
        """
        Initialize the AuthenticationManager.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager
        self.active_sessions: Dict[str, Dict] = {}
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt with 12 rounds.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: Hashed password as a string
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=self.BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def _is_account_locked(self, username: str) -> bool:
        """
        Check if an account is locked due to failed login attempts.
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if account is locked, False otherwise
        """
        query = "SELECT account_locked, failed_login_attempts FROM users WHERE username = ?"
        result = self.db.fetch_one(query, (username,))
        
        if result:
            account_locked, failed_attempts = result
            return account_locked == 1 or failed_attempts >= self.MAX_LOGIN_ATTEMPTS
        return False
    
    def _increment_failed_attempts(self, username: str) -> None:
        """
        Increment failed login attempts counter for a user.
        Locks account if max attempts reached.
        
        Args:
            username: Username to update
        """
        query = """
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1,
                account_locked = CASE 
                    WHEN failed_login_attempts + 1 >= ? THEN 1 
                    ELSE 0 
                END
            WHERE username = ?
        """
        self.db.execute_query(query, (self.MAX_LOGIN_ATTEMPTS, username))
    
    def _reset_failed_attempts(self, username: str) -> None:
        """
        Reset failed login attempts counter after successful login.
        
        Args:
            username: Username to reset
        """
        query = """
            UPDATE users 
            SET failed_login_attempts = 0, account_locked = 0
            WHERE username = ?
        """
        self.db.execute_query(query, (username,))
    
    def _create_session(self, username: str) -> str:
        """
        Create a new session for a user.
        
        Args:
            username: Username for the session
            
        Returns:
            str: Session ID
        """
        session_id = secrets.token_urlsafe(32)
        current_time = datetime.now()
        
        # Store session in memory
        self.active_sessions[session_id] = {
            'username': username,
            'created_at': current_time,
            'last_activity': current_time
        }
        
        # Store session in database
        query = """
            INSERT INTO sessions (session_id, username, created_at, last_activity)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_query(
            query,
            (session_id, username, current_time, current_time)
        )
        
        return session_id
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Optional[Dict]: Session info if successful, None otherwise
        """
        # Check if account is locked
        if self._is_account_locked(username):
            print(f"Account locked for user: {username}")
            return None
        
        # Fetch user from database
        query = "SELECT username, password_hash, role FROM users WHERE username = ?"
        user = self.db.fetch_one(query, (username,))
        
        if not user:
            print(f"User not found: {username}")
            return None
        
        db_username, password_hash, role = user
        
        # Verify password
        if not self.verify_password(password, password_hash):
            print(f"Invalid password for user: {username}")
            self._increment_failed_attempts(username)
            return None
        
        # Reset failed attempts on successful login
        self._reset_failed_attempts(username)
        
        # Create session
        session_id = self._create_session(username)
        
        return {
            'session_id': session_id,
            'username': username,
            'role': role,
            'login_time': datetime.now()
        }
    
    def logout(self, session_id: str) -> bool:
        """
        Logout a user by invalidating their session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            bool: True if logout successful, False otherwise
        """
        # Remove from memory
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Remove from database
        query = "DELETE FROM sessions WHERE session_id = ?"
        return self.db.execute_query(query, (session_id,))
    
    def is_session_valid(self, session_id: str) -> bool:
        """
        Check if a session is valid and not expired.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        if session_id not in self.active_sessions:
            # Try to load from database
            query = "SELECT username, last_activity FROM sessions WHERE session_id = ?"
            result = self.db.fetch_one(query, (session_id,))
            
            if not result:
                return False
            
            username, last_activity = result
            
            # Parse last_activity timestamp
            try:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)
                
                # Restore to memory
                self.active_sessions[session_id] = {
                    'username': username,
                    'last_activity': last_activity
                }
            except Exception as e:
                print(f"Error parsing session timestamp: {e}")
                return False
        
        # Check session timeout
        session = self.active_sessions[session_id]
        last_activity = session['last_activity']
        timeout = timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        
        if datetime.now() - last_activity > timeout:
            # Session expired
            self.logout(session_id)
            return False
        
        # Update last activity
        session['last_activity'] = datetime.now()
        query = "UPDATE sessions SET last_activity = ? WHERE session_id = ?"
        self.db.execute_query(query, (datetime.now(), session_id))
        
        return True
    
    def get_session_user(self, session_id: str) -> Optional[str]:
        """
        Get the username associated with a session.
        
        Args:
            session_id: Session ID to look up
            
        Returns:
            Optional[str]: Username if session valid, None otherwise
        """
        if not self.is_session_valid(session_id):
            return None
        
        return self.active_sessions[session_id]['username']
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions from memory and database.
        
        Returns:
            int: Number of sessions cleaned up
        """
        expired_sessions = []
        timeout = timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        current_time = datetime.now()
        
        # Find expired sessions
        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data['last_activity'] > timeout:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            self.logout(session_id)
        
        return len(expired_sessions)

# Made with Bob
