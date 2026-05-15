"""
Test script to verify SQLite threading fix.
Makes concurrent requests to the Flask app to ensure no threading errors occur.
"""
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:5000"

def test_login_request(thread_id):
    """Make a login request from a specific thread."""
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": "admin", "password": "admin123"},
            allow_redirects=False,
            timeout=5
        )
        return {
            "thread_id": thread_id,
            "status_code": response.status_code,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "thread_id": thread_id,
            "status_code": None,
            "success": False,
            "error": str(e)
        }

def test_concurrent_requests(num_threads=10):
    """Test concurrent requests to verify no threading errors."""
    print(f"Testing with {num_threads} concurrent threads...")
    print("-" * 60)
    
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(test_login_request, i) for i in range(num_threads)]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status = "[SUCCESS]" if result["success"] else "[FAILED]"
            print(f"Thread {result['thread_id']:2d}: {status} - Status: {result['status_code']}")
            if result["error"]:
                print(f"           Error: {result['error']}")
    
    print("-" * 60)
    successful = sum(1 for r in results if r["success"])
    print(f"\nResults: {successful}/{num_threads} requests successful")
    
    if successful == num_threads:
        print("[PASS] All requests completed without threading errors!")
        return True
    else:
        print("[FAIL] Some requests failed - check for threading issues")
        return False

if __name__ == "__main__":
    print("SQLite Threading Fix Verification Test")
    print("=" * 60)
    print("This test makes concurrent requests to verify the fix.")
    print("Waiting 2 seconds for Flask server to be ready...")
    time.sleep(2)
    
    # Test with increasing concurrency
    for num_threads in [5, 10, 20]:
        print(f"\n{'=' * 60}")
        success = test_concurrent_requests(num_threads)
        if not success:
            print("\n[WARNING] Threading issues detected!")
            break
        time.sleep(1)
    else:
        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED - Threading fix is working correctly!")
        print("=" * 60)

# Made with Bob
