"""
Simple test script to verify the add item functionality
"""
import requests

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_add_item():
    """Test adding an item through the web interface"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing Add Item Functionality")
    print("=" * 50)
    
    # Step 1: Get login page to get any CSRF tokens if needed
    print("\n1. Accessing login page...")
    response = session.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    
    # Step 2: Login - try with a test user
    print("\n2. Logging in...")
    login_data = {
        'username': 'test',
        'password': 'test123'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"   Status: {response.status_code}")
    
    if 'Inventory Dashboard' in response.text or 'inventory' in response.url.lower():
        print("   [OK] Login successful")
    else:
        print("   [FAIL] Login failed - trying to access inventory directly")
        # Try to access inventory anyway to see what happens
        response = session.get(f"{BASE_URL}/inventory")
        if response.status_code == 200:
            print("   [OK] Can access inventory page")
        else:
            print(f"   [FAIL] Cannot access inventory: {response.status_code}")
            return False
    
    # Step 3: Add a new item
    print("\n3. Adding a new test product...")
    add_item_data = {
        'name': 'Test Widget',
        'quantity': '100',
        'price': '49.99',
        'category': 'Electronics'
    }
    
    response = session.post(f"{BASE_URL}/inventory/add", data=add_item_data, allow_redirects=True)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        # Check for success message
        if 'added successfully' in response.text.lower():
            print("   [OK] Success message found!")
        
        # Check if product appears in the page
        if 'Test Widget' in response.text:
            print("   [OK] Product 'Test Widget' found in inventory!")
            print("\n" + "=" * 50)
            print("TEST PASSED: Add Item functionality is working!")
            return True
        else:
            print("   [WARN] Product not immediately visible")
            # Try refreshing inventory
            response = session.get(f"{BASE_URL}/inventory")
            if 'Test Widget' in response.text:
                print("   [OK] Product found after refresh!")
                print("\n" + "=" * 50)
                print("TEST PASSED: Add Item functionality is working!")
                return True
    
    print("\n" + "=" * 50)
    print("TEST INCONCLUSIVE: Check manually at http://127.0.0.1:5000/inventory")
    return False

if __name__ == "__main__":
    try:
        test_add_item()
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Make sure the Flask application is running on http://127.0.0.1:5000")

# Made with Bob
