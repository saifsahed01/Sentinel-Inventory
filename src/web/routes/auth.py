"""
Authentication Routes Blueprint
Handles user login, logout, and session management.
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

# Create blueprint
auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to require login for routes.
    Checks session validity using AuthenticationManager.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if session_id exists in Flask session
        session_id = session.get('session_id')
        
        if not session_id:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Validate session using AuthenticationManager
        auth_manager = current_app.config['AUTH_MANAGER']
        if not auth_manager.is_session_valid(session_id):
            # Session expired or invalid
            session.clear()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/')
def index():
    """
    Root route - redirect to login or inventory based on authentication status.
    """
    session_id = session.get('session_id')
    
    if session_id:
        auth_manager = current_app.config['AUTH_MANAGER']
        if auth_manager.is_session_valid(session_id):
            return redirect(url_for('inventory.inventory_list'))
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Display login page.
    If already logged in, redirect to inventory.
    """
    session_id = session.get('session_id')
    
    if session_id:
        auth_manager = current_app.config['AUTH_MANAGER']
        if auth_manager.is_session_valid(session_id):
            return redirect(url_for('inventory.inventory_list'))
    
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    """
    Handle login form submission.
    Authenticates user and creates session.
    """
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # Validate input
    if not username or not password:
        flash('Please provide both username and password.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Attempt login using AuthenticationManager
    auth_manager = current_app.config['AUTH_MANAGER']
    logger = current_app.config['LOGGER']
    
    try:
        result = auth_manager.login(username, password)
        
        if result:
            # Login successful
            session['session_id'] = result['session_id']
            session['username'] = result['username']
            session['role'] = result['role']
            session.permanent = True  # Use permanent session with configured timeout
            
            logger.info(f"User logged in successfully", {'username': username})
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('inventory.inventory_list'))
        else:
            # Login failed
            logger.warning(f"Failed login attempt", {'username': username})
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        flash('An error occurred during login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    Invalidates session and clears Flask session.
    """
    session_id = session.get('session_id')
    username = session.get('username', 'Unknown')
    
    if session_id:
        auth_manager = current_app.config['AUTH_MANAGER']
        logger = current_app.config['LOGGER']
        
        try:
            # Logout using AuthenticationManager
            auth_manager.logout(session_id)
            logger.info(f"User logged out", {'username': username})
        except Exception as e:
            logger.error(f"Logout error: {e}", exc_info=True)
    
    # Clear Flask session
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

# Made with Bob
