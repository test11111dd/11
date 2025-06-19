#!/usr/bin/env python3
import requests
import json
import time
import unittest
import os
from dotenv import load_dotenv
import sys

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api"
print(f"Testing backend API at: {API_URL}")

class BackendAPITest(unittest.TestCase):
    """Test suite for BitSafe crypto insurance backend API"""

    def test_01_root_endpoint(self):
        """Test the root endpoint (/api/)"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Hello World")
        print("✅ Root endpoint test passed")

    def test_02_post_status_check(self):
        """Test the POST /api/status endpoint"""
        payload = {"client_name": "BitSafe Test Client"}
        response = requests.post(f"{API_URL}/status", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["client_name"], "BitSafe Test Client")
        self.assertTrue("id" in data)
        self.assertTrue("timestamp" in data)
        print("✅ POST status check test passed")
        return data["id"]  # Return the ID for verification in the next test

    def test_03_get_status_checks(self):
        """Test the GET /api/status endpoint and verify data persistence"""
        # First create a new status check
        test_id = self.test_02_post_status_check()
        
        # Now get all status checks and verify our test entry is there
        response = requests.get(f"{API_URL}/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        
        # Find our test entry
        found = False
        for entry in data:
            if entry["id"] == test_id:
                found = True
                self.assertEqual(entry["client_name"], "BitSafe Test Client")
                break
        
        self.assertTrue(found, f"Could not find our test entry with ID {test_id}")
        print("✅ GET status checks test passed")
        print("✅ MongoDB data persistence verified")

    def test_04_cors_configuration(self):
        """Test CORS configuration"""
        headers = {
            "Origin": "http://example.com",  # A different origin
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
        
        # Options request to check CORS preflight
        response = requests.options(f"{API_URL}/", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Check CORS headers
        self.assertTrue("Access-Control-Allow-Origin" in response.headers)
        # The server is reflecting the Origin header value instead of using "*"
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://example.com")
        self.assertTrue("Access-Control-Allow-Methods" in response.headers)
        self.assertTrue("Access-Control-Allow-Headers" in response.headers)
        
        print("✅ CORS configuration test passed")

    def test_05_invalid_endpoint(self):
        """Test error handling for invalid endpoints"""
        response = requests.get(f"{API_URL}/nonexistent")
        self.assertEqual(response.status_code, 404)
        print("✅ Invalid endpoint test passed")

    def test_06_backend_accessibility(self):
        """Test that the backend is accessible from the frontend URL configuration"""
        # This test is essentially the same as the root endpoint test,
        # but we're explicitly checking that the URL from frontend/.env works
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        print(f"✅ Backend is accessible from {BACKEND_URL}")

if __name__ == "__main__":
    # Run the tests
    print("Starting BitSafe backend API tests...")
    print(f"Backend URL: {API_URL}")
    
    # Create a test suite and run it
    suite = unittest.TestSuite()
    suite.addTest(BackendAPITest("test_01_root_endpoint"))
    suite.addTest(BackendAPITest("test_02_post_status_check"))
    suite.addTest(BackendAPITest("test_03_get_status_checks"))
    suite.addTest(BackendAPITest("test_04_cors_configuration"))
    suite.addTest(BackendAPITest("test_05_invalid_endpoint"))
    suite.addTest(BackendAPITest("test_06_backend_accessibility"))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    if len(result.errors) > 0 or len(result.failures) > 0:
        print("\n=== Test Failures ===")
        for failure in result.failures:
            print(f"{failure[0]}: {failure[1]}")
        for error in result.errors:
            print(f"{error[0]}: {error[1]}")
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
        print("The BitSafe crypto insurance backend API is working correctly.")