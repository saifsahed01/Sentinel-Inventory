"""
Test script to verify the add item functionality
"""
import requests
from requests.auth import HTTPBasicAuth

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_add_item():
    """Test adding an item through the web interface"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing Add Item Functionality")
    print("=" * 50)
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("   ✓ Login successful")
    else:
        print(f"   ✗ Login failed with status code: {response.status_code}")
        return False
    
    # Step 2: Add a new item
    print("\n2. Adding a new test product...")
    add_item_data = {
        'name': 'Test Product',
        'quantity': '50',
        'price': '29.99',
        'category': 'Test Category'
    }
    
    response = session.post(f"{BASE_URL}/inventory/add", data=add_item_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("   ✓ Add item request successful")
        print(f"   Status code: {response.status_code}")
        
        # Check if redirected to inventory page
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   Redirected to: {location}")
    else:
        print(f"   ✗ Add item failed with status code: {response.status_code}")
        return False
    
    # Step 3: Verify the item was added by checking inventory page
    print("\n3. Verifying item was added...")
    response = session.get(f"{BASE_URL}/inventory")
    
    if response.status_code == 200:
        if 'Test Product' in response.text:
            print("   ✓ Product found in inventory!")
            print("   ✓ Add Item functionality is working correctly!")
            return True
        else:
            print("   ✗ Product not found in inventory")
            return False
    else:
        print(f"   ✗ Failed to load inventory page: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        success = test_add_item()
        print("\n" + "=" * 50)
        if success:
            print("TEST PASSED: Add Item functionality is working!")
        else:
            print("TEST FAILED: Add Item functionality has issues")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Make sure the Flask application is running on http://127.0.0.1:5000")

# Made with Bob
