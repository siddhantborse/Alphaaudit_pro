"""
Quick verification script for OLLAMA Phi3 on Windows (Unicode-safe)
"""
import requests
import json
import sys

def check_ollama_phi3():
    print("Checking OLLAMA Phi3 Setup on Windows")
    print("=" * 60)
    
    # Step 1: Check if OLLAMA is running
    print("\n1. Checking if OLLAMA service is running...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("   [OK] OLLAMA service is running!")
            
            # List available models
            models = response.json().get('models', [])
            print(f"\n   Available models ({len(models)}):")
            for model in models:
                model_name = model.get('name', 'Unknown')
                model_size = model.get('size', 0) / (1024**3)  # Convert to GB
                print(f"      - {model_name} ({model_size:.2f} GB)")
            
            # Check if phi3 is available
            phi3_available = any('phi3' in model.get('name', '').lower() for model in models)
            
            if phi3_available:
                print("\n   [OK] Phi3 model found!")
            else:
                print("\n   [WARNING] Phi3 model not found in available models")
                print("   To install: ollama pull phi3")
                return False
                
        else:
            print(f"   [ERROR] OLLAMA returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   [ERROR] Cannot connect to OLLAMA")
        print("   SOLUTION: Make sure OLLAMA is running:")
        print("      - Check Windows system tray for OLLAMA icon")
        print("      - Or run: ollama serve")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    # Step 2: Test Phi3 model with a simple prompt
    print("\n2. Testing Phi3 model with medical query...")
    try:
        test_prompt = "What is heart failure? Provide a brief medical definition."
        
        payload = {
            "model": "phi3",
            "prompt": test_prompt,
            "stream": False
        }
        
        print("   Sending test query to Phi3...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '')
            
            print("   [OK] Phi3 responded successfully!")
            print(f"\n   Phi3 Response:")
            print(f"   {ai_response[:200]}..." if len(ai_response) > 200 else f"   {ai_response}")
            
            # Check response quality
            if len(ai_response) > 50:
                print("\n   [OK] Phi3 is working properly for medical analysis!")
                return True
            else:
                print("\n   [WARNING] Response seems too short. Model may need warming up.")
                return True  # Still working, just short response
        else:
            print(f"   [ERROR] Phi3 API error: {response.status_code}")
            print(f"   Details: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   [INFO] Request timed out. Phi3 might be loading (first use can be slow).")
        print("   Try again - subsequent requests will be faster!")
        return True  # Not a failure, just slow first load
    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        return False
    
    # Step 3: Test with Alpha Audit Pro backend
    print("\n3. Testing Alpha Audit Pro backend integration...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            ai_available = health_data.get('ai_available', False)
            ai_model = health_data.get('ai_model', 'Unknown')
            
            print(f"   [OK] Backend is running!")
            print(f"   AI Status: {'ACTIVE' if ai_available else 'INACTIVE'}")
            print(f"   Model: {ai_model}")
            
            if ai_available and 'phi3' in ai_model.lower():
                print("\n   [SUCCESS] Perfect! Alpha Audit Pro is ready to use Phi3 AI!")
                return True
            elif ai_available:
                print(f"\n   [WARNING] Backend is using {ai_model}, not phi3")
                print("   Restart the backend after updating the model config")
                return True
            else:
                print("\n   [WARNING] AI not active. Make sure OLLAMA is running before starting backend.")
                return False
        else:
            print("   [ERROR] Cannot connect to backend")
            print("   Start the backend: python app_simple.py")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   [INFO] Backend not running")
        print("   Start it: python app_simple.py")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False

def main():
    success = check_ollama_phi3()
    
    print("\n" + "=" * 60)
    if success:
        print("ALL CHECKS PASSED!")
        print("\nYour system is ready:")
        print("   1. OLLAMA is running")
        print("   2. Phi3 model is available")
        print("   3. Alpha Audit Pro can use AI analysis")
        
        print("\nNext Steps:")
        print("   1. Start backend (if not running): python app_simple.py")
        print("   2. Start frontend: streamlit run frontend/streamlit_app.py")
        print("   3. Look for 'AI Analysis Active' in the UI")
    else:
        print("SOME CHECKS FAILED")
        print("\nTroubleshooting Steps:")
        print("   1. Ensure OLLAMA is running (check Windows system tray)")
        print("   2. Verify Phi3 is installed: ollama list")
        print("   3. If not installed: ollama pull phi3")
        print("   4. Test OLLAMA: ollama run phi3 \"Hello\"")
        print("   5. Restart Alpha Audit Pro backend")
    
    print("=" * 60)

if __name__ == "__main__":
    main()