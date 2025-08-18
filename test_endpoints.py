#!/usr/bin/env python3
"""
Test script for the new FastAPI endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_share_image():
    """Test the share image endpoint"""
    print("🔗 Testing Share Image...")
    response = requests.get(f"{BASE_URL}/share/generated_image.png")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_request_endpoint():
    """Test the general request endpoint"""
    print("📝 Testing Request Endpoint...")
    
    # Test different request types
    test_requests = [
        {
            "type": "image_info",
            "message": "Get information about all images",
            "data": {}
        },
        {
            "type": "system_status",
            "message": "Get system status",
            "data": {}
        },
        {
            "type": "custom",
            "message": "Custom test request",
            "data": {"test_key": "test_value"}
        },
        {
            "type": "general",
            "message": "General test request",
            "data": {"hello": "world"}
        }
    ]
    
    for i, test_request in enumerate(test_requests, 1):
        print(f"Test {i}: {test_request['type']}")
        response = requests.post(f"{BASE_URL}/api/request", json=test_request)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()

def main():
    print("🧪 Testing New FastAPI Endpoints")
    print("=" * 50)
    
    try:
        test_health_check()
        test_share_image()
        test_request_endpoint()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure it's running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
