#!/usr/bin/env python3
"""
MediCode AI - Competition Demo Script
=====================================

This script helps you run a polished demo for the D3CODE 2025 competition.
Focuses on "Empathy First" UI design and "Transforming Lives" impact.

Run this script to:
1. Set up the demo environment
2. Load demo data
3. Start all services
4. Guide you through the demo presentation

Author: MiniMax Agent
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path

class DemoManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:8501"
        
    def print_banner(self):
        """Print competition banner"""
        print("=" * 70)
        print("🏥 MEDICODE AI - D3CODE 2025 COMPETITION DEMO")
        print("=" * 70)
        print("🎯 Empathy-First UI Design")
        print("💰 $20B+ Healthcare Problem Solver")
        print("🌟 Transforming Clinical Documentation")
        print("=" * 70)
        print()
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'requests', 'sqlite3'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"  ❌ {package}")
        
        if missing:
            print(f"\n⚠️  Missing packages: {', '.join(missing)}")
            print("Run: pip install " + " ".join(missing))
            return False
        
        return True
    
    def setup_database(self):
        """Initialize database with demo data"""
        print("\n📊 Setting up database...")
        
        try:
            if (self.project_root / "database" / "init_db.py").exists():
                result = subprocess.run([sys.executable, "database/init_db.py"], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    print("  ✅ Database initialized successfully")
                else:
                    print(f"  ⚠️  Database warning: {result.stderr}")
            else:
                print("  ⚠️  Database init script not found - using defaults")
            
            return True
        except Exception as e:
            print(f"  ❌ Database setup failed: {e}")
            return False
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("\n🚀 Starting backend server...")
        
        try:
            # Check if backend is already running
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=2)
                if response.status_code == 200:
                    print("  ✅ Backend already running")
                    return True
            except:
                pass
            
            # Start backend
            backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "app:app", 
                "--host", "127.0.0.1", "--port", "8000", "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for startup
            for i in range(10):
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("  ✅ Backend started successfully")
                        return True
                except:
                    time.sleep(1)
            
            print("  ⚠️  Backend may be starting... continue with demo")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        print("\n🎨 Starting frontend...")
        
        try:
            # Check if frontend is already running
            try:
                response = requests.get(self.frontend_url, timeout=2)
                if response.status_code == 200:
                    print("  ✅ Frontend already running")
                    return True
            except:
                pass
            
            print("  🚀 Launching Streamlit...")
            print(f"  🌐 Frontend will open at: {self.frontend_url}")
            
            # Start frontend (this will block)
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "frontend/streamlit_app.py",
                "--server.port", "8501",
                "--server.headless", "false"
            ])
            
        except KeyboardInterrupt:
            print("\n  ⏹️  Frontend stopped by user")
        except Exception as e:
            print(f"  ❌ Failed to start frontend: {e}")
    
    def show_demo_guide(self):
        """Show the competition demo guide"""
        print("\n" + "="*70)
        print("🎭 COMPETITION DEMO GUIDE")
        print("="*70)
        
        demo_script = """
🎯 WINNING DEMO SCRIPT (5-7 minutes):

1. OPENING HOOK (30 seconds):
   "Every year, $20 billion in healthcare reimbursements are lost due to 
   incomplete medical documentation. We're solving this with MediCode AI."

2. PROBLEM STATEMENT (45 seconds):
   • Show the empathy-first UI design
   • Explain physician workflow pain points
   • Highlight documentation burden vs. patient care time

3. SOLUTION DEMO (3 minutes):
   📝 Demo Patient: "Diabetic with Kidney Disease"
   
   INPUT:
   - Diagnosis: "Type 2 Diabetes with chronic kidney disease"
   - Notes: "67-year-old patient with uncontrolled type 2 diabetes mellitus. 
            HbA1c elevated at 9.2%. Patient exhibits signs of diabetic 
            nephropathy with proteinuria and declining eGFR (45 ml/min). 
            Currently on metformin and lisinopril."
   
   📊 SHOW AI PROCESSING:
   - Real-time workflow guidance
   - Multi-stage AI analysis with progress bars
   - Professional medical-grade interface
   
   💰 HIGHLIGHT RESULTS:
   - Upgraded from E11.9 to E11.22 (HCC 18)
   - $3,500+ annual impact per patient
   - 95% confidence score
   - MEAT documentation guidance

4. IMPACT & SCALABILITY (60 seconds):
   • "Empathy-first design reduces physician burden"
   • "Scalable across entire healthcare networks"
   • "Real social impact: Better patient care + Financial recovery"

5. CLOSING (30 seconds):
   "MediCode AI transforms healthcare documentation, helping physicians 
   focus on what matters most - their patients."

🏆 COMPETITION WIN FACTORS:
✅ Solves $20B real-world problem
✅ Empathy-first UI design (competition requirement)
✅ Social impact: Transforms healthcare
✅ AI + Data ecosystems technology
✅ Measurable outcomes and ROI
✅ Professional, aesthetically appealing interface
✅ Scalable solution

💡 JUDGE APPEAL POINTS:
- Show the loading animations and professional UI
- Emphasize physician empathy and workflow integration
- Highlight the social cause (better patient care)
- Demonstrate clear financial impact
- Show technical sophistication (AI + medical data)
"""
        
        print(demo_script)
        
        input("\n📋 Press Enter when ready to start the demo...")
    
    def run_full_demo(self):
        """Run the complete demo setup"""
        self.print_banner()
        
        # Check system readiness
        if not self.check_dependencies():
            print("\n❌ Please install missing dependencies first")
            return False
        
        # Setup database
        if not self.setup_database():
            print("\n⚠️  Database issues detected - demo may have limited data")
        
        # Start backend
        if not self.start_backend():
            print("\n❌ Backend failed to start")
            return False
        
        # Show demo guide
        self.show_demo_guide()
        
        # Start frontend (this will block until stopped)
        self.start_frontend()
        
        return True

def main():
    """Main demo execution"""
    demo = DemoManager()
    
    # Quick mode vs full demo
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("🚀 Quick start mode...")
        demo.print_banner()
        demo.start_backend()
        time.sleep(2)
        demo.start_frontend()
    else:
        demo.run_full_demo()

if __name__ == "__main__":
    main()