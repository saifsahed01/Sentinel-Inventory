"""
Database Manager Module
Handles all database operations with secure parameterized queries.
"""
import sqlite3
import os
from typing import Optional, List, Tuple, Any


class DatabaseManager:
    """
    Manages database connections and operations with security best practices.
    All queries use parameterized statements to prevent SQL injection.
    """
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def connect(self) -> bool:
        """
        Establish connection to the database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Initialize database with required tables if they don't exist.
        Creates users and products tables with proper schema.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            # Create users table with proper schema
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sessions table for session management
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            """)
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            return False
    
    def execute_query(self, query: str, params: Tuple = ()) -> bool:
        """
        Execute a query that doesn't return results (INSERT, UPDATE, DELETE).
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            query: SQL query with ? placeholders
            params: Tuple of parameters to bind to the query
            
        Returns:
            bool: True if execution successful, False otherwise
        """
        if not self.connection or not self.cursor:
            return False
        
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            self.connection.rollback()
            return False
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """
        Execute a query and fetch one result.
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            query: SQL query with ? placeholders
            params: Tuple of parameters to bind to the query
            
        Returns:
            Optional[Tuple]: Single row result or None
        """
        if not self.connection or not self.cursor:
            return None
        
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Query fetch error: {e}")
            return None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Execute a query and fetch all results.
        Uses parameterized queries to prevent SQL injection.
        
        Args:
            query: SQL query with ? placeholders
            params: Tuple of parameters to bind to the query
            
        Returns:
            List[Tuple]: List of result rows, empty list if error
        """
        if not self.connection or not self.cursor:
            return []
        
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Query fetch error: {e}")
            return []
    
    def close(self) -> None:
        """
        Close the database connection safely.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.commit()
            self.connection.close()
        self.cursor = None
        self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# Made with Bob
