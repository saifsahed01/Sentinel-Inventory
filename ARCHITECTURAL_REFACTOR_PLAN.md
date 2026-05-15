# Architectural Refactor Plan: Inventory Management System

**Plan Date:** May 15, 2026  
**Current Version:** v1.0 (Legacy)  
**Target Version:** v2.0 (Refactored)  
**Prepared By:** Bob (Senior Software Engineer)  
**Status:** 🔴 PLANNING PHASE - DO NOT IMPLEMENT YET

---

## Executive Summary

This document outlines a comprehensive architectural refactor plan to transform the legacy monolithic inventory management system into a secure, maintainable, and scalable application. The refactor addresses **critical security vulnerabilities** identified in the Technical Debt Assessment, implements modern software engineering practices, and establishes a foundation for future enterprise growth.

**Key Objectives:**
- ✅ Eliminate all SQL injection vulnerabilities
- ✅ Implement secure password storage with industry-standard hashing
- ✅ Separate concerns using modular architecture (MVC pattern)
- ✅ Apply Object-Oriented Programming principles
- ✅ Establish proper error handling and logging infrastructure
- ✅ Enable testability and maintainability

---

## Table of Contents

1. [New Architecture Overview](#new-architecture-overview)
2. [File Structure & Organization](#file-structure--organization)
3. [Code Migration Mapping](#code-migration-mapping)
4. [Security Improvements](#security-improvements)
5. [OOP Design](#oop-design)
6. [Dependencies & Libraries](#dependencies--libraries)
7. [Implementation Guidelines](#implementation-guidelines)
8. [Testing Strategy](#testing-strategy)
9. [Migration Path](#migration-path)

---

## New Architecture Overview

### Architectural Pattern: Layered MVC Architecture

The refactored system follows a **layered Model-View-Controller (MVC)** architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                    src/ui/cli.py                            │
│              (User Interface & Input/Output)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                    │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  src/logic/      │  │  src/logic/      │                │
│  │  inventory.py    │  │  auth.py         │                │
│  │  (Inventory Ops) │  │  (Authentication)│                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                      │
│                    src/data/database.py                      │
│              (Database Operations & Queries)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                         DATABASE                             │
│                      inventory.db                            │
│                    (SQLite Database)                         │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles Applied

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Components receive dependencies rather than creating them
3. **Single Responsibility Principle**: Each class/function does one thing well
4. **Open/Closed Principle**: Open for extension, closed for modification
5. **DRY (Don't Repeat Yourself)**: Eliminate code duplication
6. **Security by Design**: Security built into every layer

---

## File Structure & Organization

### New Project Structure

```
inventory-management-system/
│
├── src/                          # Source code directory
│   ├── __init__.py              # Package initializer
│   │
│   ├── data/                    # Data Access Layer
│   │   ├── __init__.py
│   │   └── database.py          # Database operations & connection management
│   │
│   ├── logic/                   # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication & authorization logic
│   │   └── inventory.py         # Inventory business logic (OOP classes)
│   │
│   ├── ui/                      # Presentation Layer
│   │   ├── __init__.py
│   │   └── cli.py               # Command-line interface
│   │
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   ├── validators.py        # Input validation functions
│   │   ├── logger.py            # Logging configuration
│   │   └── config.py            # Configuration management
│   │
│   └── main.py                  # Application entry point
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_auth.py
│   ├── test_inventory.py
│   └── test_integration.py
│
├── config/                      # Configuration files
│   ├── config.yaml              # Application configuration
│   └── .env.example             # Environment variables template
│
├── docs/                        # Documentation
│   ├── API.md                   # API documentation
│   ├── SETUP.md                 # Setup instructions
│   └── ARCHITECTURE.md          # Architecture documentation
│
├── legacy_app/                  # Original legacy code (preserved)
│   ├── inventory.py
│   ├── inventory.db
│   └── README.txt
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in version control)
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

### File Responsibilities

| File | Responsibility | Lines of Code (Est.) |
|------|---------------|---------------------|
| [`src/main.py`](src/main.py) | Application entry point, initialization | ~50 |
| [`src/data/database.py`](src/data/database.py) | Database connection, parameterized queries | ~200 |
| [`src/logic/auth.py`](src/logic/auth.py) | User authentication, password hashing | ~150 |
| [`src/logic/inventory.py`](src/logic/inventory.py) | Inventory operations, business logic | ~300 |
| [`src/ui/cli.py`](src/ui/cli.py) | User interface, menu system | ~250 |
| [`src/utils/validators.py`](src/utils/validators.py) | Input validation functions | ~100 |
| [`src/utils/logger.py`](src/utils/logger.py) | Logging configuration | ~50 |
| [`src/utils/config.py`](src/utils/config.py) | Configuration management | ~80 |

**Total Estimated Lines:** ~1,180 lines (vs. 189 in legacy)

---

## Code Migration Mapping

### Overview: From Monolith to Modular

The legacy [`inventory.py`](legacy_app/inventory.py:1-189) file contains 189 lines of procedural code mixing database operations, business logic, authentication, and UI. This will be refactored into 8 focused modules.

### Migration Table

| Legacy Code Section | Lines | Migrates To | New Implementation |
|---------------------|-------|-------------|-------------------|
| Database initialization | 18-38 | [`src/data/database.py`](src/data/database.py) | `DatabaseManager.initialize_database()` |
| Login authentication | 41-55 | [`src/logic/auth.py`](src/logic/auth.py) | `AuthenticationManager.login()` |
| View all products | 74-84 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.get_all_products()` |
| Add product | 86-96 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.add_product()` |
| Update quantity | 98-106 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.update_quantity()` |
| Search products | 108-124 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.search_products()` |
| Low stock report | 126-137 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.get_low_stock_products()` |
| Delete product | 139-146 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.delete_product()` |
| Custom query (REMOVED) | 148-163 | N/A | Security risk - feature removed |
| Backup data | 167-175 | [`src/logic/inventory.py`](src/logic/inventory.py) | `InventoryManager.export_to_json()` |
| Main menu loop | 57-186 | [`src/ui/cli.py`](src/ui/cli.py) | `CLIInterface.run()` |
| Global variables | 6-12 | [`src/utils/config.py`](src/utils/config.py) | Configuration class |


### Detailed Migration: Database Layer

**From:** [`legacy_app/inventory.py`](legacy_app/inventory.py:18-38)
```python
# Legacy: Direct connection, no parameterization
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
cursor.execute("CREATE TABLE products ...")
```

**To:** [`src/data/database.py`](src/data/database.py)
```python
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def get_connection(self):
        """Get database connection with context manager"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute parameterized query safely"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def initialize_database(self):
        """Create tables with proper schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Products table with timestamps
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity >= 0),
                    price REAL NOT NULL CHECK(price >= 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Users table with password hashing
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked BOOLEAN DEFAULT 0
                )
            """)
            
            conn.commit()
```

**Key Improvements:**
- ✅ Context managers for automatic connection cleanup
- ✅ Parameterized queries throughout
- ✅ Database constraints (CHECK, NOT NULL, UNIQUE)
- ✅ Timestamp tracking for audit trail
- ✅ Account lockout support in schema

---

### Detailed Migration: Authentication Layer

**From:** [`legacy_app/inventory.py`](legacy_app/inventory.py:41-55)
```python
# Legacy: SQL injection vulnerability, plaintext passwords
username = input("Username: ")
password = input("Password: ")
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
```

**To:** [`src/logic/auth.py`](src/logic/auth.py)
```python
import bcrypt
from typing import Optional
from datetime import datetime, timedelta

class User:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role
    
    def is_admin(self) -> bool:
        return self.role == 'admin'

class Session:
    def __init__(self, username: str, role: str, timeout_minutes: int = 30):
        self.username = username
        self.role = role
        self.login_time = datetime.now()
        self.last_activity = datetime.now()
        self.timeout_minutes = timeout_minutes
    
    def is_expired(self) -> bool:
        timeout = timedelta(minutes=self.timeout_minutes)
        return datetime.now() - self.last_activity > timeout
    
    def update_activity(self):
        self.last_activity = datetime.now()

class AuthenticationManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_session: Optional[Session] = None
        self.max_failed_attempts = 5
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user with secure password verification"""
        # Check if account is locked
        if self.is_account_locked(username):
            raise AuthenticationError("Account locked due to too many failed attempts")
        
        # Parameterized query
        query = "SELECT username, password_hash, role FROM users WHERE username = ?"
        result = self.db.execute_query(query, (username,))
        
        if not result:
            self.increment_failed_attempts(username)
            return False
        
        user_data = result[0]
        if self.verify_password(password, user_data[1]):
            self.current_session = Session(user_data[0], user_data[2])
            self.reset_failed_attempts(username)
            self.update_last_login(username)
            return True
        
        self.increment_failed_attempts(username)
        return False
```

**Key Improvements:**
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Parameterized authentication query
- ✅ Session management with timeout
- ✅ Account lockout after 5 failed attempts
- ✅ Last login tracking

---

### Detailed Migration: Inventory Business Logic

**From:** [`legacy_app/inventory.py`](legacy_app/inventory.py:86-96)
```python
# Legacy: SQL injection, no validation
prod_id = input("Enter Product ID: ")
prod_name = input("Enter Product Name: ")
prod_qty = input("Enter Quantity: ")
prod_price = input("Enter Price: ")
query = "INSERT INTO products VALUES (" + prod_id + ", '" + prod_name + "', " + prod_qty + ", " + prod_price + ")"
cursor.execute(query)
```

**To:** [`src/logic/inventory.py`](src/logic/inventory.py)
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class Product:
    """Product data model"""
    id: int
    name: str
    quantity: int
    price: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_low_stock(self, threshold: int = 5) -> bool:
        return self.quantity < threshold
    
    def calculate_value(self) -> float:
        return self.quantity * self.price

class InventoryManager:
    def __init__(self, db_manager, low_stock_threshold: int = 5):
        self.db = db_manager
        self.low_stock_threshold = low_stock_threshold
    
    def add_product(self, product: Product) -> bool:
        """Add product with validation and parameterized query"""
        # Validate inputs
        from src.utils.validators import (
            validate_product_id, validate_product_name,
            validate_quantity, validate_price
        )
        
        validate_product_id(str(product.id))
        validate_product_name(product.name)
        validate_quantity(str(product.quantity))
        validate_price(str(product.price))
        
        # Check for duplicate ID
        if self.get_product_by_id(product.id):
            raise InventoryException(f"Product ID {product.id} already exists")
        
        # Parameterized insert
        query = """
            INSERT INTO products (id, name, quantity, price, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.execute_update(
            query,
            (product.id, product.name, product.quantity, product.price,
             datetime.now().isoformat(), datetime.now().isoformat())
        )
        return True
    
    def get_all_products(self) -> List[Product]:
        """Retrieve all products"""
        query = "SELECT id, name, quantity, price, created_at, updated_at FROM products ORDER BY id"
        results = self.db.execute_query(query)
        return [Product(*row) for row in results]
    
    def search_products(self, search_term: str) -> List[Product]:
        """Search with parameterized query"""
        query = """
            SELECT id, name, quantity, price, created_at, updated_at
            FROM products
            WHERE name LIKE ? OR CAST(id AS TEXT) = ?
        """
        results = self.db.execute_query(query, (f"%{search_term}%", search_term))
        return [Product(*row) for row in results]
    
    def export_to_json(self, filepath: str) -> bool:
        """Export data to JSON (replaces pickle)"""
        products = self.get_all_products()
        data = {
            'export_date': datetime.now().isoformat(),
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'quantity': p.quantity,
                    'price': p.price
                }
                for p in products
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
```

**Key Improvements:**
- ✅ OOP design with Product class
- ✅ Input validation before database operations
- ✅ Parameterized queries for all operations
- ✅ JSON export instead of pickle
- ✅ Business logic methods (is_low_stock, calculate_value)

---

## Security Improvements

### 1. SQL Injection Prevention

**Critical Vulnerabilities Fixed:**

| Legacy Line | Vulnerability | Fix |
|-------------|--------------|-----|
| 45-46 | Login authentication | Parameterized query in [`auth.py`](src/logic/auth.py) |
| 93-94 | Product insertion | Parameterized query in [`inventory.py`](src/logic/inventory.py) |
| 103-104 | Quantity update | Parameterized query in [`inventory.py`](src/logic/inventory.py) |
| 112-114 | Product search | Parameterized query in [`inventory.py`](src/logic/inventory.py) |
| 143-144 | Product deletion | Parameterized query in [`inventory.py`](src/logic/inventory.py) |

**Before (Vulnerable):**
```python
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```

**After (Secure):**
```python
query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
cursor.execute(query, (username, password_hash))
```

**Attack Prevention:**
- ✅ Prevents authentication bypass (`admin' OR '1'='1`)
- ✅ Prevents data extraction (UNION attacks)
- ✅ Prevents data manipulation (UPDATE/DELETE injection)
- ✅ Prevents privilege escalation

---

### 2. Password Security Implementation

**Bcrypt Configuration:**
```python
# In src/logic/auth.py
import bcrypt

# Hash password with 12 rounds (industry standard)
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

# Verify password (constant-time comparison)
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
```

**Password Policy:**
- Minimum 8 characters
- Must contain uppercase letter
- Must contain lowercase letter
- Must contain number
- Must contain special character
- Cannot be common password (dictionary check)

**Database Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- Stores bcrypt hash
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked BOOLEAN DEFAULT 0,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

### 3. Input Validation Framework

**Validation Functions in [`src/utils/validators.py`](src/utils/validators.py):**

```python
class ValidationError(Exception):
    pass

def validate_product_id(value: str) -> int:
    """Validate product ID"""
    try:
        product_id = int(value)
        if product_id <= 0:
            raise ValidationError("Product ID must be positive")
        if product_id > 999999:
            raise ValidationError("Product ID too large")
        return product_id
    except ValueError:
        raise ValidationError("Product ID must be a number")

def validate_quantity(value: str) -> int:
    """Validate quantity"""
    try:
        quantity = int(value)
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if quantity > 1000000:
            raise ValidationError("Quantity exceeds maximum")
        return quantity
    except ValueError:
        raise ValidationError("Quantity must be a number")

def validate_price(value: str) -> float:
    """Validate price"""
    try:
        price = float(value)
        if price < 0:
            raise ValidationError("Price cannot be negative")
        if price > 999999.99:
            raise ValidationError("Price exceeds maximum")
        return round(price, 2)
    except ValueError:
        raise ValidationError("Price must be a number")

def validate_product_name(value: str) -> str:
    """Validate product name"""
    if not value or len(value.strip()) == 0:
        raise ValidationError("Product name cannot be empty")
    if len(value) > 100:
        raise ValidationError("Product name too long (max 100 characters)")
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(f"Invalid character: {char}")
    
    return value.strip()
```

**Validation Rules:**
- ✅ Product ID: 1-999999
- ✅ Quantity: 0-1000000
- ✅ Price: 0.00-999999.99
- ✅ Product Name: 1-100 characters, no special characters
- ✅ Username: 3-50 characters, alphanumeric + underscore
- ✅ Password: 8+ characters with complexity requirements

---

### 4. Session Management

**Session Features:**
```python
class Session:
    def __init__(self, username: str, role: str, timeout_minutes: int = 30):
        self.username = username
        self.role = role
        self.login_time = datetime.now()
        self.last_activity = datetime.now()
        self.timeout_minutes = timeout_minutes
    
    def is_expired(self) -> bool:
        """Check if session expired (30 minutes of inactivity)"""
        timeout = timedelta(minutes=self.timeout_minutes)
        return datetime.now() - self.last_activity > timeout
    
    def update_activity(self):
        """Update last activity on each action"""
        self.last_activity = datetime.now()
```

**Security Features:**
- ✅ 30-minute inactivity timeout
- ✅ Activity-based timeout refresh
- ✅ Account lockout after 5 failed attempts
- ✅ Automatic logout on timeout
- ✅ Session duration tracking
- ✅ Audit logging of all auth events

---

### 5. Removed Security Risks

**Features Removed:**

1. **Custom Query Execution** (lines 148-163)
   - **Risk:** Allows arbitrary SQL execution
   - **Impact:** Complete database control, data destruction
   - **Alternative:** Admin users use database tools directly

2. **Pickle Serialization** (lines 172-174)
   - **Risk:** Insecure deserialization, remote code execution
   - **Impact:** Malicious code execution, system compromise
   - **Alternative:** JSON export with integrity verification

3. **Hardcoded Credentials** (lines 7-8, 26-27)
   - **Risk:** Universal access, credential rotation impossible
   - **Impact:** Unauthorized access, insider threats
   - **Alternative:** Environment variables + bcrypt hashing

---

## OOP Design

### Class Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         Product                               │
├──────────────────────────────────────────────────────────────┤
│ - id: int                                                     │
│ - name: str                                                   │
│ - quantity: int                                               │
│ - price: float                                                │
│ - created_at: datetime                                        │
│ - updated_at: datetime                                        │
├──────────────────────────────────────────────────────────────┤
│ + is_low_stock(threshold: int) -> bool                        │
│ + calculate_value() -> float                                  │
│ + to_dict() -> dict                                           │
│ + from_dict(data: dict) -> Product                            │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ manages
                            │
┌──────────────────────────────────────────────────────────────┐
│                    InventoryManager                           │
├──────────────────────────────────────────────────────────────┤
│ - db: DatabaseManager                                         │
│ - low_stock_threshold: int                                    │
├──────────────────────────────────────────────────────────────┤
│ + get_all_products() -> List[Product]                         │
│ + get_product_by_id(id: int) -> Optional[Product]            │
│ + add_product(product: Product) -> bool                       │
│ + update_quantity(id: int, quantity: int) -> bool            │
│ + delete_product(id: int) -> bool                            │
│ + search_products(term: str) -> List[Product]                │
│ + get_low_stock_products() -> List[Product]                  │
│ + export_to_json(filepath: str) -> bool                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                           User                                │
├──────────────────────────────────────────────────────────────┤
│ - username: str                                               │
│ - role: str                                                   │
├──────────────────────────────────────────────────────────────┤
│ + is_admin() -> bool                                          │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ manages
                            │
┌──────────────────────────────────────────────────────────────┐
│                  AuthenticationManager                        │
├──────────────────────────────────────────────────────────────┤
│ - db: DatabaseManager                                         │
│ - current_session: Optional[Session]                          │
│ - max_failed_attempts: int                                    │
├──────────────────────────────────────────────────────────────┤
│ + login(username: str, password: str) -> bool                │
│ + logout()                                                    │
│ + hash_password(password: str) -> str                        │
│ + verify_password(password: str, hash: str) -> bool          │
│ + check_session() -> bool                                    │
│ + create_user(username, password, role) -> bool              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     DatabaseManager                           │
├──────────────────────────────────────────────────────────────┤
│ - db_path: str                                                │
├──────────────────────────────────────────────────────────────┤
│ + get_connection() -> Connection                              │
│ + execute_query(query: str, params: tuple) -> List[tuple]    │
│ + execute_update(query: str, params: tuple) -> int           │
│ + initialize_database()                                       │
│ + seed_initial_data()                                         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                       CLIInterface                            │
├──────────────────────────────────────────────────────────────┤
│ - auth_manager: AuthenticationManager                         │
│ - inventory_manager: InventoryManager                         │
├──────────────────────────────────────────────────────────────┤
│ + run()                                                       │
│ + display_main_menu()                                         │
│ + handle_login() -> bool                                      │
│ + handle_view_products()                                      │
│ + handle_add_product()                                        │
│ + handle_update_quantity()                                    │
│ + handle_search_products()                                    │
│ + handle_low_stock_report()                                   │
│ + handle_delete_product()                                     │
│ + handle_export_data()                                        │
└──────────────────────────────────────────────────────────────┘
```

### Key OOP Principles Applied

1. **Encapsulation**: Data and methods bundled in classes
2. **Single Responsibility**: Each class has one clear purpose
3. **Dependency Injection**: Classes receive dependencies via constructor
4. **Composition over Inheritance**: Managers compose database access
5. **Data Classes**: Product uses `@dataclass` for clean data modeling

---

## Dependencies & Libraries

### Required Python Packages

**[`requirements.txt`](requirements.txt):**
```txt
# Security
bcrypt==4.1.2              # Password hashing
python-dotenv==1.0.0       # Environment variable management

# Database
# sqlite3 is built-in to Python

# Data handling
pyyaml==6.0.1              # Configuration file parsing

# Testing
pytest==7.4.3              # Testing framework
pytest-cov==4.1.0          # Code coverage
pytest-mock==3.12.0        # Mocking support

# Code quality
pylint==3.0.3              # Linting
black==23.12.1             # Code formatting
mypy==1.7.1                # Type checking

# Development
ipython==8.18.1            # Enhanced REPL
```

### Library Justification

| Library | Purpose | Why This Choice |
|---------|---------|----------------|
| **bcrypt** | Password hashing | Industry standard, slow by design (prevents brute force), automatic salt generation |
| **python-dotenv** | Environment variables | Secure configuration management, 12-factor app compliance |
| **pyyaml** | Configuration parsing | Human-readable config files, widely supported |
| **pytest** | Testing framework | Most popular Python testing tool, excellent plugin ecosystem |
| **pylint** | Code quality | Comprehensive linting, enforces best practices |
| **black** | Code formatting | Opinionated formatter, eliminates style debates |
| **mypy** | Type checking | Static type checking, catches bugs before runtime |

### Installation Commands

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

---

## Implementation Guidelines

### Phase 1: Foundation (Week 1)

**Priority: Critical Security Fixes**

1. **Setup Project Structure**
   - Create directory structure
   - Initialize git repository
   - Setup virtual environment
   - Install dependencies

2. **Implement Database Layer** ([`src/data/database.py`](src/data/database.py))
   - DatabaseManager class
   - Parameterized query methods
   - Connection management
   - Schema initialization

3. **Implement Authentication** ([`src/logic/auth.py`](src/logic/auth.py))
   - Password hashing with bcrypt
   - Secure authentication
   - Session management
   - Account lockout

4. **Implement Validation** ([`src/utils/validators.py`](src/utils/validators.py))
   - Input validation functions
   - Custom validation exceptions
   - Sanitization helpers

**Deliverables:**
- ✅ All SQL injection vulnerabilities fixed
- ✅ Password hashing implemented
- ✅ Input validation in place
- ✅ Unit tests for security features

---

### Phase 2: Business Logic (Week 2)

**Priority: Core Functionality**

1. **Implement Product Model** ([`src/logic/inventory.py`](src/logic/inventory.py))
   - Product dataclass
   - Business logic methods
   - Serialization support

2. **Implement Inventory Manager** ([`src/logic/inventory.py`](src/logic/inventory.py))
   - CRUD operations
   - Search functionality
   - Low stock reporting
   - JSON export

3. **Implement Configuration** ([`src/utils/config.py`](src/utils/config.py))
   - Environment variable loading
   - Configuration validation
   - Default values

4. **Implement Logging** ([`src/utils/logger.py`](src/utils/logger.py))
   - Structured logging
   - Log rotation
   - Audit trail

**Deliverables:**
- ✅ All business logic migrated
- ✅ OOP design implemented
- ✅ Logging infrastructure in place
- ✅ Integration tests passing

---

### Phase 3: User Interface (Week 3)

**Priority: User Experience**

1. **Implement CLI Interface** ([`src/ui/cli.py`](src/ui/cli.py))
   - Menu system
   - Input handling
   - Output formatting
   - Error display

2. **Implement Main Entry Point** ([`src/main.py`](src/main.py))
   - Application initialization
   - Dependency injection
   - Graceful shutdown
   - Error handling

3. **Create Documentation**
   - README.md
   - SETUP.md
   - API.md
   - ARCHITECTURE.md

**Deliverables:**
- ✅ Complete CLI interface
- ✅ User-friendly error messages
- ✅ Comprehensive documentation
- ✅ End-to-end tests passing

---

### Phase 4: Testing & Quality (Week 4)

**Priority: Reliability**

1. **Unit Tests**
   - Test all classes and methods
   - Mock database operations
   - Test edge cases
   - Achieve 80%+ coverage

2. **Integration Tests**
   - Test component interactions
   - Test database operations
   - Test authentication flow
   - Test error handling

3. **Code Quality**
   - Run pylint (score > 9.0)
   - Run mypy (no type errors)
   - Format with black
   - Review and refactor

**Deliverables:**
- ✅ 80%+ test coverage
- ✅ All tests passing
- ✅ Code quality metrics met
- ✅ Production-ready code

---

## Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_database.py         # Database layer tests
├── test_auth.py             # Authentication tests
├── test_inventory.py        # Inventory logic tests
├── test_validators.py       # Validation tests
├── test_cli.py              # UI tests
└── test_integration.py      # End-to-end tests
```

### Test Coverage Goals

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| [`database.py`](src/data/database.py) | 90% | Critical |
| [`auth.py`](src/logic/auth.py) | 95% | Critical |
| [`inventory.py`](src/logic/inventory.py) | 85% | High |
| [`validators.py`](src/utils/validators.py) | 100% | High |
| [`cli.py`](src/ui/cli.py) | 70% | Medium |
| [`config.py`](src/utils/config.py) | 80% | Medium |

### Sample Test Cases

**Security Tests ([`test_auth.py`](tests/test_auth.py)):**
```python
def test_sql_injection_prevention():
    """Test that SQL injection is prevented"""
    auth = AuthenticationManager(db)
    # Attempt SQL injection
    result = auth.login("admin' OR '1'='1", "anything")
    assert result is False

def test_password_hashing():
    """Test password is hashed, not stored plaintext"""
    auth = AuthenticationManager(db)
    auth.create_user("testuser", "password123", "user")
    # Verify password is hashed in database
    query = "SELECT password_hash FROM users WHERE username = ?"
    result = db.execute_query(query, ("testuser",))
    assert result[0][0] != "password123"
    assert result[0][0].startswith("$2b$")  # bcrypt hash

def test_account_lockout():
    """Test account locks after failed attempts"""
    auth = AuthenticationManager(db)
    # Attempt 5 failed logins
    for _ in range(5):
        auth.login("admin", "wrongpassword")
    # 6th attempt should raise exception
    with pytest.raises(AuthenticationError):
        auth.login("admin", "wrongpassword")
```

**Validation Tests ([`test_validators.py`](tests/test_validators.py)):**
```python
def test_negative_quantity_rejected():
    """Test negative quantities are rejected"""
    with pytest.raises(ValidationError):
        validate_quantity("-5")

def test_sql_injection_in_product_name():
    """Test SQL injection attempts in product name"""
    with pytest.raises(ValidationError):
        validate_product_name("Product'; DROP TABLE products;--")

def test_price_precision():
    """Test price is rounded to 2 decimal places"""
    price = validate_price("19.999")
    assert price == 20.00
```

---

## Migration Path

### Step-by-Step Migration Process

#### Step 1: Backup Current System
```bash
# Backup database
cp legacy_app/inventory.db legacy_app/inventory.db.backup

# Backup code
cp legacy_app/inventory.py legacy_app/inventory.py.backup
```

#### Step 2: Setup New Structure
```bash
# Create new directory structure
mkdir -p src/{data,logic,ui,utils}
mkdir -p tests config docs

# Initialize Python packages
touch src/__init__.py
touch src/data/__init__.py
touch src/logic/__init__.py
touch src/ui/__init__.py
touch src/utils/__init__.py
```

#### Step 3: Migrate Data
```bash
# Export existing data
python legacy_app/inventory.py
# Select option 8 (Backup Data)

# Convert pickle to JSON (manual script needed)
python scripts/convert_backup.py
```

#### Step 4: Initialize New Database
```python
# Run database initialization
from src.data.database import DatabaseManager
from src.logic.auth import AuthenticationManager

db = DatabaseManager("inventory.db")
db.initialize_database()

# Migrate users with hashed passwords
auth = AuthenticationManager(db)
auth.create_user("admin", "password123", "admin")
auth.create_user("user1", "pass123", "user")
```

#### Step 5: Import Data
```python
# Import products from JSON
from src.logic.inventory import InventoryManager
inventory = InventoryManager(db)
inventory.import_from_json("backup.json")
```

#### Step 6: Testing
```bash
# Run all tests
pytest tests/ -v --cov=src

# Run specific security tests
pytest tests/test_auth.py -v
```

#### Step 7: Deployment
```bash
# Run new application
python src/main.py
```

### Rollback Plan

If issues arise:
1. Stop new application
2. Restore backup database: `cp legacy_app/inventory.db.backup legacy_app/inventory.db`
3. Run legacy application: `python legacy_app/inventory.py`
4. Investigate and fix issues
5. Retry migration

---

## Summary

### What's Being Built

A **secure, modular, maintainable** inventory management system with:

- ✅ **8 focused modules** (vs. 1 monolithic file)
- ✅ **Zero SQL injection vulnerabilities** (parameterized queries throughout)
- ✅ **Bcrypt password hashing** (industry-standard security)
- ✅ **Comprehensive input validation** (prevents data corruption)
- ✅ **Session management** (30-minute timeout, account lockout)
- ✅ **OOP design** (Product, InventoryManager, AuthenticationManager classes)
- ✅ **Structured logging** (audit trail, troubleshooting)
- ✅ **JSON export** (replaces insecure pickle)
- ✅ **80%+ test coverage** (reliability and confidence)
- ✅ **Complete documentation** (maintainability)

### Key Architectural Decisions

1. **Layered MVC Architecture**: Clear separation of concerns
2. **Dependency Injection**: Testable, flexible components
3. **Parameterized Queries**: SQL injection prevention
4. **Bcrypt Hashing**: Secure password storage
5. **JSON Serialization**: Safe data export
6. **Comprehensive Validation**: Data integrity
7. **Structured Logging**: Audit trail and troubleshooting
8. **Feature Removal**: Eliminated security risks (custom queries, pickle)

### Estimated Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Foundation | 1 week | 40 hours |
| Phase 2: Business Logic | 1 week | 40 hours |
| Phase 3: User Interface | 1 week | 40 hours |
| Phase 4: Testing & Quality | 1 week | 40 hours |
| **Total** | **4 weeks** | **160 hours** |

### Success Criteria

- ✅ All critical security vulnerabilities eliminated
- ✅ All unit tests passing (80%+ coverage)
- ✅ All integration tests passing
- ✅ Code quality metrics met (pylint > 9.0)
- ✅ Documentation complete
- ✅ User acceptance testing passed
- ✅ Performance benchmarks met
- ✅ Security audit passed

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Get approval** for implementation approach
3. **Allocate resources** (developer time, testing environment)
4. **Setup development environment** (git repo, CI/CD)
5. **Begin Phase 1** implementation
6. **Schedule regular reviews** (weekly progress checks)

---

**Plan Status:** ✅ COMPLETE - READY FOR REVIEW

**Prepared By:** Bob, Senior Software Engineer  
**Date:** May 15, 2026  
**Version:** 1.0
