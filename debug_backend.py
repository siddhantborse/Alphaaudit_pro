#!/usr/bin/env python3
"""
Backend Debug Test
=================

Quick test to see what's causing the 422 error
"""

import requests
import json

def test_backend():
    """Test the backend with exact data format"""
    
    # Test 1: Health check
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test 2: Simple analyze request
    print("\n🧪 Testing analyze endpoint...")
    
    # Exact data format that backend expects
    test_data = {
        "primary_diagnosis": "Type 2 Diabetes",
        "clinical_notes": "Patient has diabetes with elevated blood sugar",
        "current_icd": None,
        "patient_history": "Age: 67, Encounter: Annual Wellness Visit"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/analyze", 
            json=test_data,
            timeout=30
        )
        
        print(f"Analyze response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Suggestions: {len(data.get('suggestions', []))}")
            print(f"Extracted conditions: {data.get('extracted_conditions', {})}")
        
        elif response.status_code == 422:
            print("❌ 422 Validation Error:")
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        
        else:
            print(f"❌ Error {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_backend()