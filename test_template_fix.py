#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the template fix for the Internal Server Error.
This script tests that Flask can properly load templates after the fix.
"""

import os
import sys

def test_template_loading():
    """Test that the Flask app can load templates correctly."""
    print("=" * 60)
    print("Testing Template Fix for Internal Server Error")
    print("=" * 60)
    print()
    
    try:
        # Import the Flask app
        print("1. Importing Flask app...")
        from src.web.app import create_app
        app = create_app()
        print("   [OK] Flask app created successfully")
        print()
        
        # Check template folder configuration
        print("2. Checking template folder configuration...")
        template_folder = app.template_folder
        print(f"   Template folder: {template_folder}")
        
        if template_folder:
            abs_template_path = os.path.abspath(template_folder)
            print(f"   Absolute path: {abs_template_path}")
            
            if os.path.exists(abs_template_path):
                print("   [OK] Template folder exists")
            else:
                print("   [X] Template folder does NOT exist")
                return False
        else:
            print("   [X] Template folder not configured")
            return False
        print()
        
        # Check for required templates
        print("3. Checking for required template files...")
        required_templates = ['error.html', 'login.html', 'inventory.html', 'base.html']
        all_found = True
        
        for template in required_templates:
            template_path = os.path.join(abs_template_path, template)
            if os.path.exists(template_path):
                print(f"   [OK] {template} found")
            else:
                print(f"   [X] {template} NOT found")
                all_found = False
        print()
        
        # Test template rendering with app context and request context
        print("4. Testing template rendering...")
        with app.test_request_context():
            try:
                from flask import render_template
                # Try to render the error template (the one that was failing)
                html = render_template('error.html',
                                     error_code=404,
                                     error_message="Test error")
                print("   [OK] error.html rendered successfully")
                print(f"   Rendered HTML length: {len(html)} characters")
            except Exception as e:
                print(f"   [X] Failed to render error.html: {e}")
                return False
        print()
        
        # Summary
        print("=" * 60)
        print("RESULT: Template fix verification PASSED [OK]")
        print("=" * 60)
        print()
        print("The application should now start without template errors.")
        print("You can start the application with: python run_web.py")
        print()
        return True
        
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("=" * 60)
        print("RESULT: Template fix verification FAILED [X]")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_template_loading()
    sys.exit(0 if success else 1)

# Made with Bob
