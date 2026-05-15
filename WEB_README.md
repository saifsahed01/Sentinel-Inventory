# Web Interface Guide

## Overview

The Flask web interface provides a modern, browser-based alternative to the command-line interface for the Inventory Management System. It offers an intuitive way to manage inventory items, user authentication, and system operations through a web browser.

The web interface is built using Flask, a lightweight Python web framework, and reuses the existing business logic from `src/logic/` to ensure consistency with the CLI application.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

Install all required dependencies including Flask and its components:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (>=3.0.0) - Web framework
- Werkzeug (>=3.0.0) - WSGI utility library
- bcrypt - Password hashing
- python-dotenv - Environment configuration
- PyYAML - Configuration file support
- And other core dependencies

## Running the Web Server

### Start the Server

To start the web server, run the following command from the project root directory:

```bash
python run_web.py
```

The server will start and display output similar to:

```
 * Serving Flask app 'app'
 * Debug mode: on/off
 * Running on http://0.0.0.0:5000
```

### Access the Application

Once the server is running, open your web browser and navigate to:

```
http://localhost:5000
```

Or from another machine on the same network:

```
http://<your-ip-address>:5000
```

### Stop the Server

To stop the web server, press `Ctrl+C` in the terminal where the server is running.

## Login Instructions

### Using Existing Credentials

The web interface uses the same user database as the CLI application. You can log in with any existing user credentials:

1. Navigate to `http://localhost:5000`
2. You will be redirected to the login page
3. Enter your username and password
4. Click "Login"

### Default Credentials

If you're using the system for the first time, you may need to create a user account through the CLI first:

```bash
python src/main.py
# Select option to register a new user
```

Alternatively, if a default admin account exists in your database, use those credentials.

## Available Features

### 1. User Authentication
- **Login**: Secure authentication using bcrypt password hashing
- **Session Management**: Maintains user sessions across requests
- **Logout**: Securely end your session

### 2. Inventory Management
- **View Inventory**: Browse all inventory items in a clean, tabular format
- **Item Details**: View detailed information for each item including:
  - Item ID
  - Name
  - Quantity
  - Price
  - Category
  - Last updated timestamp

### 3. User Interface
- **Responsive Design**: Works on desktop and mobile browsers
- **Navigation**: Easy-to-use navigation menu
- **Flash Messages**: Real-time feedback for user actions
- **Session Indicators**: Shows logged-in user information

## Architecture

### Design Principles

The web interface follows a clean architecture pattern:

```
run_web.py (Entry Point)
    ↓
src/web/app.py (Flask Application Factory)
    ↓
src/web/routes/ (Route Handlers)
    ↓
src/logic/ (Business Logic - Shared with CLI)
    ↓
src/data/ (Database Layer)
```

### Code Reuse

The web interface **reuses existing business logic** from `src/logic/`:

- **Authentication Logic** (`src/logic/auth.py`): User login, password verification, session management
- **Inventory Logic** (`src/logic/inventory.py`): Item retrieval, inventory operations
- **Database Layer** (`src/data/database.py`): Shared database connection and queries

This ensures:
- **Consistency**: Same behavior between CLI and web interfaces
- **Maintainability**: Single source of truth for business rules
- **Reliability**: Well-tested logic shared across interfaces

### Project Structure

```
src/web/
├── __init__.py           # Package initialization
├── app.py                # Flask application factory
├── routes/               # Route handlers
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   └── inventory.py     # Inventory routes
└── templates/            # HTML templates
    ├── base.html        # Base template with common layout
    ├── login.html       # Login page
    └── inventory.html   # Inventory listing page
```

## Troubleshooting

### Port Already in Use

**Problem**: Error message "Address already in use" when starting the server.

**Solution**: 
- Another application is using port 5000
- Stop the other application or change the port in `run_web.py`:
  ```python
  app.run(host="0.0.0.0", port=5001, debug=app.config.get("DEBUG", False))
  ```

### Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: 
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're using the correct Python environment

### Database Not Found

**Problem**: Error about missing database file.

**Solution**:
- Ensure the database file exists at `data/inventory.db`
- Run the CLI application first to initialize the database: `python src/main.py`
- Check the `.env` file for correct database path configuration

### Login Fails

**Problem**: Cannot log in with credentials.

**Solution**:
- Verify credentials are correct
- Ensure user exists in the database
- Create a new user through the CLI if needed
- Check logs in `logs/` directory for detailed error messages

### Template Not Found

**Problem**: `TemplateNotFound` error.

**Solution**:
- Ensure all template files exist in `src/web/templates/`
- Check that Flask is looking in the correct template directory
- Verify file names match exactly (case-sensitive)

### Static Files Not Loading

**Problem**: CSS or JavaScript files not loading.

**Solution**:
- Check browser console for 404 errors
- Ensure static files are in the correct directory
- Clear browser cache and reload

### Debug Mode Issues

**Problem**: Need to see detailed error messages.

**Solution**:
- Set `DEBUG=True` in your `.env` file
- Restart the web server
- Check `logs/` directory for detailed application logs

## Configuration

### Environment Variables

The web application uses environment variables for configuration. Create or modify `.env` file:

```env
# Database configuration
DATABASE_PATH=data/inventory.db

# Flask configuration
DEBUG=False
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
```

### Security Notes

- **Never** run with `DEBUG=True` in production
- Use a strong, random `SECRET_KEY` in production
- Consider using HTTPS in production environments
- Regularly update dependencies for security patches

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Project README**: See `README.md` for overall project information
- **CLI Guide**: See `PHASE1_README.md` for CLI usage
- **Architecture**: See `ARCHITECTURAL_REFACTOR_PLAN.md` for system design

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs in `logs/` directory
3. Consult the main project documentation
4. Check existing issues in the project repository