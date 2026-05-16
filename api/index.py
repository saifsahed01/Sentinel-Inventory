"""
Vercel Serverless Function Entry Point
This file serves as the entry point for Vercel's serverless deployment.
Enhanced with comprehensive error logging and diagnostics.
"""
import sys
import os
import traceback

# Print startup diagnostics
print("=" * 80)
print("VERCEL SERVERLESS FUNCTION STARTUP")
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
    print(f"✓ Added project root to Python path: {project_root}")
except Exception as e:
    print(f"✗ ERROR adding project root to path: {e}")
    traceback.print_exc()

# Initialize app variable
app = None

try:
    print("\n" + "=" * 80)
    print("STEP 1: Importing Flask")
    print("=" * 80)
    from flask import Flask
    print("✓ Flask imported successfully")
    
    print("\n" + "=" * 80)
    print("STEP 2: Testing minimal Flask app")
    print("=" * 80)
    
    # Create a minimal test app first
    test_app = Flask(__name__)
    
    @test_app.route('/')
    def hello():
        return {'status': 'ok', 'message': 'Minimal Flask app works!'}
    
    @test_app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'python_version': sys.version,
            'cwd': os.getcwd(),
            'database_path': os.getenv('DATABASE_PATH', 'NOT SET'),
            'log_directory': os.getenv('LOG_DIRECTORY', 'NOT SET')
        }
    
    print("✓ Minimal Flask app created successfully")
    
    print("\n" + "=" * 80)
    print("STEP 3: Importing application modules")
    print("=" * 80)
    
    try:
        print("  Importing src.web.app...")
        from src.web.app import create_app
        print("  ✓ src.web.app imported successfully")
        
        print("\n" + "=" * 80)
        print("STEP 4: Creating full Flask application")
        print("=" * 80)
        
        # Try to create the full app
        app = create_app()
        print("✓ Full Flask application created successfully")
        
    except Exception as e:
        print(f"\n✗ ERROR creating full Flask app: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("FALLBACK: Using minimal Flask app")
        print("=" * 80)
        
        # Fall back to minimal app if full app fails
        app = test_app
        
        # Add error endpoint
        @app.route('/error-info')
        def error_info():
            return {
                'status': 'error',
                'message': 'Full app initialization failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        
        print("✓ Fallback to minimal app successful")

except Exception as e:
    print(f"\n✗ CRITICAL ERROR during initialization: {e}")
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
                'message': 'Critical initialization error',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        
        print("✓ Emergency app created")
    except Exception as emergency_error:
        print(f"✗ FATAL: Cannot even create emergency app: {emergency_error}")
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
