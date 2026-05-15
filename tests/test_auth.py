"""
Unit Tests for AuthenticationManager
Tests authentication, password hashing, session management, and security features.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import bcrypt

from src.logic.auth import AuthenticationManager


class TestAuthenticationManager:
    """Test suite for AuthenticationManager class."""
    
    def test_should_initialize_with_database_manager(self, mock_db):
        """
        Test that AuthenticationManager initializes correctly with a database manager.
        Validates that the instance is created and active_sessions dict is initialized.
        """
        auth_manager = AuthenticationManager(mock_db)
        
        assert auth_manager.db == mock_db
        assert isinstance(auth_manager.active_sessions, dict)
        assert len(auth_manager.active_sessions) == 0
    
    def test_should_hash_password_successfully(self, auth_manager_with_mocks):
        """
        Test that password hashing works correctly using bcrypt.
        Validates that the hash is different from the original password
        and follows bcrypt format.
        """
        password = "TestPassword123!"
        hashed = auth_manager_with_mocks.hash_password(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert hashed.startswith('$2b$')  # bcrypt hash format
        assert len(hashed) == 60  # bcrypt hash length
    
    def test_should_verify_correct_password(self, auth_manager_with_mocks):
        """
        Test that password verification succeeds with correct password.
        Validates that a password matches its hash.
        """
        password = "TestPassword123!"
        password_hash = auth_manager_with_mocks.hash_password(password)
        
        result = auth_manager_with_mocks.verify_password(password, password_hash)
        
        assert result is True
    
    def test_should_fail_verification_with_wrong_password(self, auth_manager_with_mocks):
        """
        Test that password verification fails with incorrect password (edge case).
        Validates security by ensuring wrong passwords are rejected.
        """
        correct_password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = auth_manager_with_mocks.hash_password(correct_password)
        
        result = auth_manager_with_mocks.verify_password(wrong_password, password_hash)
        
        assert result is False
    
    def test_should_handle_invalid_hash_in_verification(self, auth_manager_with_mocks):
        """
        Test that password verification handles invalid hash gracefully (edge case).
        Validates error handling for corrupted or invalid hash data.
        """
        password = "TestPassword123!"
        invalid_hash = "not_a_valid_bcrypt_hash"
        
        result = auth_manager_with_mocks.verify_password(password, invalid_hash)
        
        assert result is False
    
    def test_should_login_successfully_with_correct_credentials(self, auth_manager_with_mocks, sample_user_data):
        """
        Test successful login with correct username and password.
        Validates that a session is created and user information is returned.
        """
        username = sample_user_data['username']
        password = sample_user_data['password']
        password_hash = sample_user_data['password_hash']
        role = sample_user_data['role']
        
        # Mock database responses
        auth_manager_with_mocks.db.fetch_one.side_effect = [
            (0, 0),  # _is_account_locked: not locked, 0 failed attempts
            (username, password_hash, role)  # login: user data
        ]
        
        result = auth_manager_with_mocks.login(username, password)
        
        assert result is not None
        assert 'session_id' in result
        assert result['username'] == username
        assert result['role'] == role
        assert 'login_time' in result
        assert len(auth_manager_with_mocks.active_sessions) == 1
    
    def test_should_fail_login_with_wrong_password(self, auth_manager_with_mocks, sample_user_data):
        """
        Test that login fails with incorrect password (edge case).
        Validates that failed login attempts are tracked and session is not created.
        """
        username = sample_user_data['username']
        wrong_password = "WrongPassword999!"
        password_hash = sample_user_data['password_hash']
        role = sample_user_data['role']
        
        # Mock database responses
        auth_manager_with_mocks.db.fetch_one.side_effect = [
            (0, 0),  # _is_account_locked: not locked
            (username, password_hash, role)  # login: user data
        ]
        
        result = auth_manager_with_mocks.login(username, wrong_password)
        
        assert result is None
        assert len(auth_manager_with_mocks.active_sessions) == 0
        # Verify that failed attempts were incremented
        auth_manager_with_mocks.db.execute_query.assert_called()
    
    def test_should_fail_login_with_nonexistent_username(self, auth_manager_with_mocks):
        """
        Test that login fails with non-existent username (edge case).
        Validates that the system handles unknown users gracefully.
        """
        username = "nonexistent_user"
        password = "SomePassword123!"
        
        # Mock database responses
        auth_manager_with_mocks.db.fetch_one.side_effect = [
            (0, 0),  # _is_account_locked: not locked
            None  # login: user not found
        ]
        
        result = auth_manager_with_mocks.login(username, password)
        
        assert result is None
        assert len(auth_manager_with_mocks.active_sessions) == 0
    
    def test_should_prevent_login_when_account_locked(self, auth_manager_with_mocks, sample_user_data):
        """
        Test that login is prevented when account is locked due to failed attempts.
        Validates account lockout security feature.
        """
        username = sample_user_data['username']
        password = sample_user_data['password']
        
        # Mock account as locked
        auth_manager_with_mocks.db.fetch_one.return_value = (1, 5)  # locked=1, 5 failed attempts
        
        result = auth_manager_with_mocks.login(username, password)
        
        assert result is None
        assert len(auth_manager_with_mocks.active_sessions) == 0
    
    def test_should_increment_failed_login_attempts(self, auth_manager_with_mocks):
        """
        Test that failed login attempts are incremented correctly.
        Validates the security tracking mechanism.
        """
        username = "testuser"
        
        auth_manager_with_mocks._increment_failed_attempts(username)
        
        # Verify database update was called with correct parameters
        auth_manager_with_mocks.db.execute_query.assert_called_once()
        call_args = auth_manager_with_mocks.db.execute_query.call_args
        assert username in call_args[0][1]
    
    def test_should_reset_failed_attempts_after_successful_login(self, auth_manager_with_mocks, sample_user_data):
        """
        Test that failed login attempts are reset after successful login.
        Validates that the counter is cleared on successful authentication.
        """
        username = sample_user_data['username']
        password = sample_user_data['password']
        password_hash = sample_user_data['password_hash']
        role = sample_user_data['role']
        
        # Mock database responses
        auth_manager_with_mocks.db.fetch_one.side_effect = [
            (0, 3),  # _is_account_locked: not locked, but has 3 failed attempts
            (username, password_hash, role)  # login: user data
        ]
        
        result = auth_manager_with_mocks.login(username, password)
        
        assert result is not None
        # Verify reset was called (should be in the execute_query calls)
        assert auth_manager_with_mocks.db.execute_query.call_count >= 2
    
    def test_should_create_session_with_unique_id(self, auth_manager_with_mocks):
        """
        Test that session creation generates a unique session ID.
        Validates session management functionality.
        """
        username = "testuser"
        
        session_id = auth_manager_with_mocks._create_session(username)
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 20  # URL-safe token should be reasonably long
        assert session_id in auth_manager_with_mocks.active_sessions
        assert auth_manager_with_mocks.active_sessions[session_id]['username'] == username
    
    def test_should_logout_successfully(self, auth_manager_with_mocks):
        """
        Test that logout removes session correctly.
        Validates session cleanup functionality.
        """
        username = "testuser"
        session_id = auth_manager_with_mocks._create_session(username)
        
        result = auth_manager_with_mocks.logout(session_id)
        
        assert result is True
        assert session_id not in auth_manager_with_mocks.active_sessions
        auth_manager_with_mocks.db.execute_query.assert_called()
    
    def test_should_validate_active_session(self, auth_manager_with_mocks):
        """
        Test that valid sessions are recognized as active.
        Validates session validation logic.
        """
        username = "testuser"
        session_id = auth_manager_with_mocks._create_session(username)
        
        is_valid = auth_manager_with_mocks.is_session_valid(session_id)
        
        assert is_valid is True
    
    def test_should_invalidate_nonexistent_session(self, auth_manager_with_mocks):
        """
        Test that non-existent sessions are invalid (edge case).
        Validates security by rejecting unknown session IDs.
        """
        fake_session_id = "nonexistent_session_123"
        
        # Mock database to return None for non-existent session
        auth_manager_with_mocks.db.fetch_one.return_value = None
        
        is_valid = auth_manager_with_mocks.is_session_valid(fake_session_id)
        
        assert is_valid is False
    
    def test_should_invalidate_expired_session(self, auth_manager_with_mocks):
        """
        Test that expired sessions are invalidated (edge case).
        Validates session timeout functionality.
        """
        username = "testuser"
        session_id = auth_manager_with_mocks._create_session(username)
        
        # Manually set last_activity to expired time
        expired_time = datetime.now() - timedelta(minutes=AuthenticationManager.SESSION_TIMEOUT_MINUTES + 1)
        auth_manager_with_mocks.active_sessions[session_id]['last_activity'] = expired_time
        
        is_valid = auth_manager_with_mocks.is_session_valid(session_id)
        
        assert is_valid is False
        assert session_id not in auth_manager_with_mocks.active_sessions
    
    def test_should_update_last_activity_on_validation(self, auth_manager_with_mocks):
        """
        Test that session validation updates last activity timestamp.
        Validates that active sessions stay alive with continued use.
        """
        username = "testuser"
        session_id = auth_manager_with_mocks._create_session(username)
        
        original_time = auth_manager_with_mocks.active_sessions[session_id]['last_activity']
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        auth_manager_with_mocks.is_session_valid(session_id)
        
        updated_time = auth_manager_with_mocks.active_sessions[session_id]['last_activity']
        assert updated_time > original_time
    
    def test_should_get_username_from_valid_session(self, auth_manager_with_mocks):
        """
        Test retrieving username from a valid session.
        Validates session-to-user mapping functionality.
        """
        username = "testuser"
        session_id = auth_manager_with_mocks._create_session(username)
        
        retrieved_username = auth_manager_with_mocks.get_session_user(session_id)
        
        assert retrieved_username == username
    
    def test_should_return_none_for_invalid_session_user(self, auth_manager_with_mocks):
        """
        Test that getting user from invalid session returns None (edge case).
        Validates error handling for invalid session lookups.
        """
        fake_session_id = "invalid_session_456"
        
        # Mock database to return None
        auth_manager_with_mocks.db.fetch_one.return_value = None
        
        retrieved_username = auth_manager_with_mocks.get_session_user(fake_session_id)
        
        assert retrieved_username is None
    
    def test_should_cleanup_expired_sessions(self, auth_manager_with_mocks):
        """
        Test that expired sessions are cleaned up in batch.
        Validates maintenance functionality for session management.
        """
        # Create multiple sessions
        session1 = auth_manager_with_mocks._create_session("user1")
        session2 = auth_manager_with_mocks._create_session("user2")
        session3 = auth_manager_with_mocks._create_session("user3")
        
        # Expire two sessions
        expired_time = datetime.now() - timedelta(minutes=AuthenticationManager.SESSION_TIMEOUT_MINUTES + 1)
        auth_manager_with_mocks.active_sessions[session1]['last_activity'] = expired_time
        auth_manager_with_mocks.active_sessions[session2]['last_activity'] = expired_time
        
        cleaned_count = auth_manager_with_mocks.cleanup_expired_sessions()
        
        assert cleaned_count == 2
        assert session1 not in auth_manager_with_mocks.active_sessions
        assert session2 not in auth_manager_with_mocks.active_sessions
        assert session3 in auth_manager_with_mocks.active_sessions
    
    def test_should_handle_account_lockout_at_max_attempts(self, auth_manager_with_mocks):
        """
        Test that account is locked when max failed attempts reached.
        Validates the account lockout threshold enforcement.
        """
        username = "testuser"
        
        # Mock account at max attempts threshold
        auth_manager_with_mocks.db.fetch_one.return_value = (0, AuthenticationManager.MAX_LOGIN_ATTEMPTS)
        
        is_locked = auth_manager_with_mocks._is_account_locked(username)
        
        assert is_locked is True
    
    def test_should_restore_session_from_database(self, auth_manager_with_mocks):
        """
        Test that sessions can be restored from database if not in memory.
        Validates session persistence across application restarts.
        """
        session_id = "restored_session_789"
        username = "testuser"
        last_activity = datetime.now().isoformat()
        
        # Mock database to return session data
        auth_manager_with_mocks.db.fetch_one.return_value = (username, last_activity)
        
        is_valid = auth_manager_with_mocks.is_session_valid(session_id)
        
        assert is_valid is True
        assert session_id in auth_manager_with_mocks.active_sessions
        assert auth_manager_with_mocks.active_sessions[session_id]['username'] == username
    
    def test_should_handle_malformed_timestamp_in_session(self, auth_manager_with_mocks):
        """
        Test that malformed timestamps in session data are handled gracefully (edge case).
        Validates error handling for corrupted session data.
        """
        session_id = "malformed_session_999"
        username = "testuser"
        invalid_timestamp = "not_a_valid_timestamp"
        
        # Mock database to return invalid timestamp
        auth_manager_with_mocks.db.fetch_one.return_value = (username, invalid_timestamp)
        
        is_valid = auth_manager_with_mocks.is_session_valid(session_id)
        
        assert is_valid is False

# Made with Bob
