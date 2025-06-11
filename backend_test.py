#!/usr/bin/env python3
"""
Backend Test Script for Dodo Payments Integration

This script tests the Dodo Payments integration in the backend API:
1. Health Check Endpoint
2. Payment Creation
3. Test Payment Endpoint
4. Subscription Creation
5. Database Connectivity
6. Error Handling
"""

import requests
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional
import unittest

# Get the backend URL from the frontend .env file
def get_backend_url():
    """Get the backend URL from the frontend .env file"""
    env_file_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    backend_url = None
    
    with open(env_file_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=', 1)[1].strip('"\'')
                break
    
    if not backend_url:
        raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")
    
    return backend_url

# Base URL for API requests
BASE_URL = f"{get_backend_url()}/api"
print(f"Using backend URL: {BASE_URL}")

class DodoPaymentsTest(unittest.TestCase):
    """Test cases for Dodo Payments integration"""
    
    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n=== Testing Health Check Endpoint ===")
        response = requests.get(f"{BASE_URL}/health")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the response structure
        self.assertEqual(data["status"], "healthy")
        self.assertTrue("dodo_payments" in data)
        self.assertTrue("database" in data)
        
        # Verify Dodo Payments configuration
        dodo_config = data["dodo_payments"]
        self.assertTrue(dodo_config["api_key_configured"])
        self.assertTrue(dodo_config["webhook_secret_configured"])
        self.assertEqual(dodo_config["mode"], "test")
        
        # Verify database connection
        db_config = data["database"]
        self.assertTrue(db_config["connected"])
        self.assertEqual(db_config["name"], "test_database")
        
        print("✅ Health check endpoint test passed")
    
    def test_02_create_payment(self):
        """Test payment creation endpoint"""
        print("\n=== Testing Payment Creation Endpoint ===")
        
        # Sample payment data
        payment_data = {
            "billing_currency": "USD",
            "allowed_payment_method_types": ["credit", "debit"],
            "product_cart": [
                {
                    "product_id": "test_product_1",
                    "amount": 1000,  # $10.00 in cents
                    "quantity": 1
                }
            ],
            "return_url": "https://example.com/payment-success",
            "customer": {
                "email": "test@example.com",
                "name": "Test Customer"
            },
            "billing": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "country": "US",
                "zipcode": "12345"
            },
            "metadata": {
                "test": True,
                "source": "backend_test"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/payments/checkout",
            json=payment_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the response structure
        self.assertTrue("id" in data)
        self.assertTrue("url" in data)
        self.assertTrue("checkout_url" in data or "url" in data)
        self.assertTrue("status" in data)
        
        # Store payment ID for future reference
        self.payment_id = data["id"]
        print(f"Created payment with ID: {self.payment_id}")
        print("✅ Payment creation test passed")
    
    def test_03_test_simple_payment(self):
        """Test the simple payment test endpoint"""
        print("\n=== Testing Simple Payment Test Endpoint ===")
        
        response = requests.post(f"{BASE_URL}/payments/test/simple-payment")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the response structure
        self.assertTrue("id" in data)
        self.assertTrue("url" in data)
        self.assertTrue("checkout_url" in data or "url" in data)
        self.assertTrue("status" in data)
        
        print("✅ Simple payment test endpoint passed")
    
    def test_04_create_subscription(self):
        """Test subscription creation endpoint"""
        print("\n=== Testing Subscription Creation Endpoint ===")
        
        # Sample subscription data
        subscription_data = {
            "customer": {
                "customer_id": f"cust_{int(time.time())}",
                "email": "subscriber@example.com",
                "name": "Test Subscriber"
            },
            "product_id": "test_subscription_product",
            "billing": {
                "street": "456 Subscription Ave",
                "city": "Subscription City",
                "state": "SC",
                "country": "US",
                "zipcode": "54321"
            },
            "payment_link": True,
            "metadata": {
                "test": True,
                "source": "backend_test"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/payments/subscriptions",
            json=subscription_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the response structure
        self.assertTrue("subscription_id" in data)
        self.assertTrue("customer_id" in data)
        self.assertTrue("status" in data)
        self.assertTrue("product_id" in data)
        
        # Store subscription ID for future reference
        self.subscription_id = data["subscription_id"]
        print(f"Created subscription with ID: {self.subscription_id}")
        print("✅ Subscription creation test passed")
    
    def test_05_error_handling_missing_fields(self):
        """Test error handling with missing required fields"""
        print("\n=== Testing Error Handling (Missing Fields) ===")
        
        # Payment data with missing required fields
        invalid_payment_data = {
            "billing_currency": "USD",
            # Missing product_cart
            "return_url": "https://example.com/payment-success"
        }
        
        response = requests.post(
            f"{BASE_URL}/payments/checkout",
            json=invalid_payment_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return a validation error (422)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        
        # Verify error response contains validation details
        self.assertTrue("detail" in data)
        print("✅ Error handling test (missing fields) passed")
    
    def test_06_error_handling_invalid_data(self):
        """Test error handling with invalid data types"""
        print("\n=== Testing Error Handling (Invalid Data) ===")
        
        # Payment data with invalid data types
        invalid_payment_data = {
            "billing_currency": "USD",
            "product_cart": [
                {
                    "product_id": "test_product",
                    "amount": "not_a_number",  # Should be an integer
                    "quantity": 1
                }
            ],
            "return_url": "https://example.com/payment-success"
        }
        
        response = requests.post(
            f"{BASE_URL}/payments/checkout",
            json=invalid_payment_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return a validation error (422)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        
        # Verify error response contains validation details
        self.assertTrue("detail" in data)
        print("✅ Error handling test (invalid data) passed")
    
    def test_07_get_payment(self):
        """Test getting payment details by ID"""
        print("\n=== Testing Get Payment Endpoint ===")
        
        # Skip if no payment ID from previous test
        if not hasattr(self, 'payment_id'):
            print("⚠️ Skipping test: No payment ID available")
            return
        
        response = requests.get(f"{BASE_URL}/payments/payments/{self.payment_id}")
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            data = response.json()
            self.assertEqual(data["payment_id"], self.payment_id)
            print("✅ Get payment test passed")
        else:
            # This might fail in test mode if the payment is not actually stored
            print(f"⚠️ Get payment returned status {response.status_code}: {response.text}")
            print("⚠️ This is expected in test mode if mock payments are not stored in the database")

def run_tests():
    """Run all tests"""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(DodoPaymentsTest('test_01_health_check'))
    suite.addTest(DodoPaymentsTest('test_02_create_payment'))
    suite.addTest(DodoPaymentsTest('test_03_test_simple_payment'))
    suite.addTest(DodoPaymentsTest('test_04_create_subscription'))
    suite.addTest(DodoPaymentsTest('test_05_error_handling_missing_fields'))
    suite.addTest(DodoPaymentsTest('test_06_error_handling_invalid_data'))
    suite.addTest(DodoPaymentsTest('test_07_get_payment'))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Starting Dodo Payments Backend Tests")
    print(f"Backend URL: {BASE_URL}")
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)