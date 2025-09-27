#!/usr/bin/env python3
"""
Quick test script to verify HCC Assistant is working correctly
Run this after setting up the project to ensure everything is functional
"""

import requests
import sys
import json
from typing import Dict, Any

def test_api_endpoint(url: str, method: str = "GET", data: Dict = None) -> bool:
    """Test an API endpoint and return success status"""
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {method} {url} - Success")
            return True
        else:
            print(f"❌ {method} {url} - Failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {method} {url} - Error: {str(e)}")
        return False

def test_database():
    """Test database functionality"""
    print("\n📋 Testing Database...")
    try:
        from database.models import DatabaseManager
        db = DatabaseManager()
        
        # Test search functionality
        results = db.search_by_keywords(["diabetes", "kidney"])
        if results:
            print(f"✅ Database search working - Found {len(results)} results")
            return True
        else:
            print("❌ Database search returned no results")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def test_ai_client():
    """Test AI client (OLLAMA)"""
    print("\n🤖 Testing AI Client...")
    try:
        from ai.ollama_client import OllamaClient
        client = OllamaClient()
        
        if client.is_available():
            print("✅ OLLAMA is running and available")
            
            # Test extraction
            test_text = "Patient has diabetes with kidney disease"
            result = client.extract_medical_conditions(test_text)
            if result:
                print(f"✅ AI extraction working - Found: {result.get('primary_condition')}")
                return True
        else:
            print("⚠️ OLLAMA not available (will use fallback mode)")
            return True  # Not critical for demo
    except Exception as e:
        print(f"⚠️ AI client issue: {str(e)} (fallback mode will be used)")
        return True  # Not critical

def test_full_workflow():
    """Test complete workflow with sample data"""
    print("\n🔄 Testing Full Workflow...")
    
    # Sample request
    test_request = {
        "primary_diagnosis": "diabetes",
        "clinical_notes": "Patient has type 2 diabetes with chronic kidney disease stage 3",
        "current_icd": "E11.9",
        "patient_history": "Long-standing diabetes"
    }
    
    api_url = "http://localhost:8000/analyze"
    
    try:
        response = requests.post(api_url, json=test_request, timeout=30)
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get('suggestions', [])
            if suggestions:
                best_suggestion = suggestions[0]
                print(f"✅ Full workflow working!")
                print(f"   Best suggestion: {best_suggestion['icd_code']} ({best_suggestion['hcc_description']})")
                print(f"   RAF weight: {best_suggestion['raf_weight']}")
                return True
            else:
                print("❌ Workflow completed but no suggestions returned")
                return False
        else:
            print(f"❌ Workflow failed - API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workflow test failed: {str(e)}")
        return False

def main():
    print("🚀 HCC Assistant - System Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test API endpoints
    print("\n🌐 Testing API Endpoints...")
    tests = [
        (f"{base_url}/", "GET"),
        (f"{base_url}/health", "GET"),
        (f"{base_url}/demo-scenarios", "GET"),
    ]
    
    api_success = all(test_api_endpoint(url, method) for url, method in tests)
    
    # Test components
    db_success = test_database()
    ai_success = test_ai_client()
    
    if api_success and db_success:
        workflow_success = test_full_workflow()
    else:
        workflow_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   API Endpoints: {'PASS' if api_success else 'FAIL'}")
    print(f"   Database: {'PASS' if db_success else 'FAIL'}")
    print(f"   AI Client: {'PASS' if ai_success else 'WARN'}")
    print(f"   Full Workflow: {'PASS' if workflow_success else 'FAIL'}")
    
    if api_success and db_success and workflow_success:
        print("\n🎉 All critical systems working! Ready for demo.")
        print("\n📝 Next steps:")
        print("   1. Start frontend: streamlit run frontend/streamlit_app.py")
        print("   2. Open browser: http://localhost:8501")
        print("   3. Try demo scenarios from the sidebar")
        return 0
    else:
        print("\n⚠️ Some systems need attention. Check errors above.")
        print("\n🔧 Troubleshooting:")
        if not api_success:
            print("   - Ensure backend is running: uvicorn app:app --reload")
        if not db_success:
            print("   - Reinitialize database: python database/init_db.py")
        if not workflow_success:
            print("   - Check API logs for detailed error messages")
        return 1

if __name__ == "__main__":
    sys.exit(main())
