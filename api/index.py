"""
Vercel Serverless Function Entry Point
This file serves as the entry point for Vercel's serverless deployment.
The AppLogger bug has been fixed, so the full application is now enabled.
"""
import sys
import os
import traceback

# Print startup diagnostics
print("=" * 80)
print("VERCEL SERVERLESS FUNCTION STARTUP - FULL APP ENABLED")
print("=" * 80)
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Environment variables:")
for key in ['DATABASE_PATH', 'LOG_DIRECTORY', 'DEBUG_MODE', 'FLASK_SECRET_KEY']:
    print(f"  {key}: {os.getenv(key, 'NOT SET')}")
print("=" * 80)

# Add the project root to the Python path
try:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    print(f"[OK] Added project root to Python path: {project_root}")
except Exception as e:
    print(f"[ERROR] Failed to add project root to path: {e}")
    traceback.print_exc()

# Initialize app variable
app = None

try:
    print("\n" + "=" * 80)
    print("STEP 1: Importing Flask and application modules")
    print("=" * 80)
    from flask import Flask, jsonify
    from src.web.app import create_app
    print("[OK] Flask and application modules imported successfully")
    
    print("\n" + "=" * 80)
    print("STEP 2: Creating full Flask application")
    print("=" * 80)
    
    # Create the full application (AppLogger bug is now fixed)
    app = create_app()
    print("[OK] Full Flask application created successfully")
    
    # Add health endpoint for monitoring
    @app.route('/health')
    def health():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'app': 'IBM Inventory Management System',
            'python_version': sys.version,
            'cwd': os.getcwd(),
            'database_path': os.getenv('DATABASE_PATH', 'NOT SET'),
            'log_directory': os.getenv('LOG_DIRECTORY', 'NOT SET')
        })
    
    print("[OK] Health endpoint registered")
    
    # Log all registered routes for debugging
    print("\n" + "=" * 80)
    print("REGISTERED ROUTES:")
    print("=" * 80)
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})) if rule.methods else ''
        print(f"  {rule.endpoint:30s} {methods:20s} {rule.rule}")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] CRITICAL ERROR during initialization: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    # Create emergency fallback app
    print("\n" + "=" * 80)
    print("EMERGENCY FALLBACK: Creating emergency Flask app")
    print("=" * 80)
    
    try:
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def emergency():
            return jsonify({
                'status': 'emergency_mode',
                'message': 'Critical initialization error - Full app failed to load',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'note': 'This should not happen as AppLogger bug is fixed'
            })
        
        @app.route('/health')
        def emergency_health():
            return jsonify({
                'status': 'unhealthy',
                'mode': 'emergency',
                'error': str(e)
            })
        
        print("[OK] Emergency app created")
    except Exception as emergency_error:
        print(f"[FATAL] Cannot even create emergency app: {emergency_error}")
        traceback.print_exc()
        raise

print("\n" + "=" * 80)
print("INITIALIZATION COMPLETE")
print("=" * 80)
print(f"App object: {app}")
print(f"App type: {type(app)}")
print("=" * 80 + "\n")

# Vercel expects the app to be named 'app' or to be the default export
# This is the WSGI application that Vercel will use
handler = app

# Made with Bob
