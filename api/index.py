"""
Vercel Serverless Function Entry Point
This file serves as the entry point for Vercel's serverless deployment.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.app import create_app

# Create the Flask app instance for Vercel
# Use environment variables for serverless configuration
app = create_app()

# Vercel expects the app to be named 'app' or to be the default export
# This is the WSGI application that Vercel will use
handler = app

# Made with Bob
