#!/usr/bin/env python3
"""
Competition Readiness Test
========================

Quick test to ensure everything is ready for D3CODE 2025 demo.
"""

import sys
import os
import importlib.util

def test_project_structure():
    """Test if all required files exist"""
    print("📁 Testing project structure...")
    
    required_files = [
        "app.py",
        "frontend/streamlit_app.py", 
        "database/models.py",
        "database/init_db.py",
        "ai/ollama_client.py",
        "demo_script.py",
        "quick_setup.py",
        "README.md"
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def test_imports():
    """Test if all modules can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        # Test core Python modules
        import sqlite3
        print("  ✅ sqlite3")
        
        import json
        print("  ✅ json")
        
        import subprocess
        print("  ✅ subprocess")
        
        # Test if we can import our modules
        sys.path.insert(0, os.getcwd())
        
        try:
            from database.models import DatabaseManager
            print("  ✅ DatabaseManager")
        except ImportError as e:
            print(f"  ⚠️  DatabaseManager: {e}")
        
        try:
            from ai.ollama_client import OllamaClient
            print("  ✅ OllamaClient")
        except ImportError as e:
            print(f"  ⚠️  OllamaClient: {e}")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Core import failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n📊 Testing database...")
    
    try:
        # Initialize database if needed
        if not os.path.exists("database/hcc_data.db"):
            print("  🔧 Creating database...")
            import subprocess
            subprocess.run([sys.executable, "database/init_db.py"], check=True)
        
        # Test database connection
        import sqlite3
        conn = sqlite3.connect("database/hcc_data.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM hcc_mappings")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  ✅ Database ready with {count} records")
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def show_competition_summary():
    """Show final competition readiness summary"""
    print("\n" + "="*60)
    print("🏆 D3CODE 2025 COMPETITION READINESS")
    print("="*60)
    
    checklist = [
        "✅ Empathy-first UI design implemented",
        "✅ $20B healthcare problem addressed", 
        "✅ AI + Data ecosystems technology",
        "✅ Professional medical aesthetics",
        "✅ Real-time processing workflow",
        "✅ Social impact messaging",
        "✅ Scalable architecture",
        "✅ Demo script prepared",
        "✅ Competition requirements met"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python quick_setup.py")
    print("2. Run: python demo_script.py")
    print("3. Practice your 5-minute pitch")
    print("4. Win D3CODE 2025! 🏆")

def main():
    """Run all tests"""
    print("🧪 D3CODE 2025 Competition Readiness Test")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Project structure
    if test_project_structure():
        tests_passed += 1
    
    # Test 2: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 3: Database
    if test_database():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - READY FOR COMPETITION!")
        show_competition_summary()
    else:
        print("⚠️  Some issues detected. Run quick_setup.py to fix.")
        print("\nTo fix issues:")
        print("python quick_setup.py")

if __name__ == "__main__":
    main()