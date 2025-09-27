#!/usr/bin/env python3
"""
Quick Competition Setup Script
=============================

Run this before your demo to ensure everything is working perfectly.

Usage:
    python quick_setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install all required packages"""
    print("📦 Installing requirements...")
    
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "streamlit>=1.28.0", 
        "requests>=2.31.0",
        "sqlite3",  # Usually built-in
        "pydantic>=2.0.0"
    ]
    
    for req in requirements:
        try:
            print(f"  Installing {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"  ✅ {req}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  Warning: {req} failed to install")

def create_missing_files():
    """Create any missing essential files"""
    
    # Ensure database directory exists
    os.makedirs("database", exist_ok=True)
    
    # Create minimal database init if missing
    if not os.path.exists("database/init_db.py"):
        print("📊 Creating database initialization...")
        
        db_init_content = '''
import sqlite3
import os

def init_database():
    """Initialize HCC database with sample data"""
    db_path = "database/hcc_data.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
    CREATE TABLE hcc_mappings (
        id INTEGER PRIMARY KEY,
        icd_code TEXT,
        description TEXT,
        hcc_category TEXT,
        raf_value REAL,
        annual_impact INTEGER
    )
    """)
    
    # Sample data for demo
    sample_data = [
        ("E11.22", "Type 2 diabetes mellitus with diabetic chronic kidney disease", "HCC 18", 0.302, 5134),
        ("E11.65", "Type 2 diabetes mellitus with hyperglycemia", "HCC 19", 0.104, 1768),
        ("I50.9", "Heart failure, unspecified", "HCC 85", 0.323, 5491),
        ("N18.3", "Chronic kidney disease, stage 3", "HCC 138", 0.287, 4879),
        ("F32.1", "Major depressive disorder, recurrent, moderate", "HCC 155", 0.309, 5253),
        ("Z94.0", "Kidney transplant status", "HCC 134", 0.525, 8925)
    ]
    
    cursor.executemany("""
    INSERT INTO hcc_mappings (icd_code, description, hcc_category, raf_value, annual_impact)
    VALUES (?, ?, ?, ?, ?)
    """, sample_data)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
'''
        
        with open("database/init_db.py", "w") as f:
            f.write(db_init_content)
    
    # Create minimal database models if missing
    if not os.path.exists("database/models.py"):
        print("📋 Creating database models...")
        
        models_content = '''
import sqlite3
from typing import List, Optional

class HCCMapping:
    def __init__(self, icd_code, icd_description, hcc_code, hcc_description, raf_weight, category=None):
        self.icd_code = icd_code
        self.icd_description = icd_description
        self.hcc_code = hcc_code
        self.hcc_description = hcc_description
        self.raf_weight = raf_weight
        self.category = category

class DatabaseManager:
    def __init__(self, db_path="database/hcc_data.db"):
        self.db_path = db_path
    
    def search_by_keywords(self, keywords: List[str]) -> List[HCCMapping]:
        """Search for HCC mappings by keywords"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword search
            query = "SELECT * FROM hcc_mappings WHERE "
            conditions = []
            params = []
            
            for keyword in keywords[:3]:  # Limit to first 3 keywords
                conditions.append("(description LIKE ? OR icd_code LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if conditions:
                query += " OR ".join(conditions)
                query += " ORDER BY raf_value DESC LIMIT 5"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                mappings = []
                for row in results:
                    mapping = HCCMapping(
                        icd_code=row[1],
                        icd_description=row[2],
                        hcc_code=row[3],
                        hcc_description=row[3],
                        raf_weight=row[4]
                    )
                    mappings.append(mapping)
                
                conn.close()
                return mappings
            
            conn.close()
            return []
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def get_hcc_info(self, icd_code: str) -> Optional[HCCMapping]:
        """Get HCC info for specific ICD code"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM hcc_mappings WHERE icd_code = ?", (icd_code,))
            result = cursor.fetchone()
            
            if result:
                mapping = HCCMapping(
                    icd_code=result[1],
                    icd_description=result[2],
                    hcc_code=result[3],
                    hcc_description=result[3],
                    raf_weight=result[4]
                )
                conn.close()
                return mapping
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Database error: {e}")
            return None
'''
        
        with open("database/models.py", "w") as f:
            f.write(models_content)
    
    # Create AI client if missing
    os.makedirs("ai", exist_ok=True)
    if not os.path.exists("ai/ollama_client.py"):
        print("🤖 Creating AI client...")
        
        ai_content = '''
import json
from typing import Dict, List

class OllamaClient:
    def __init__(self):
        self.available = False
        
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        return self.available
    
    def extract_medical_conditions(self, text: str) -> Dict:
        """Extract medical conditions from text (fallback method)"""
        # Simple keyword extraction for demo
        keywords = []
        medical_terms = [
            'diabetes', 'kidney', 'heart', 'failure', 'depression',
            'chronic', 'acute', 'severe', 'moderate', 'transplant'
        ]
        
        text_lower = text.lower()
        for term in medical_terms:
            if term in text_lower:
                keywords.append(term)
        
        # Determine chronicity
        chronicity = 'chronic' if 'chronic' in text_lower else 'acute'
        
        # Determine severity
        severity = 'severe' if 'severe' in text_lower else 'moderate' if 'moderate' in text_lower else 'mild'
        
        # Extract primary condition
        primary_condition = 'diabetes' if 'diabetes' in text_lower else 'heart failure' if 'heart' in text_lower else 'depression' if 'depression' in text_lower else 'unknown'
        
        return {
            'medical_keywords': keywords,
            'extracted_terms': keywords,
            'chronicity': chronicity,
            'severity': severity,
            'primary_condition': primary_condition,
            'secondary_conditions': keywords[1:3] if len(keywords) > 1 else []
        }
'''
        
        with open("ai/ollama_client.py", "w") as f:
            f.write(ai_content)
        
        # Create __init__.py files
        with open("ai/__init__.py", "w") as f:
            f.write("")
        with open("database/__init__.py", "w") as f:
            f.write("")

def setup_competition_ready():
    """Set up everything for competition"""
    print("🏆 D3CODE 2025 Competition Setup")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Create missing files
    create_missing_files()
    
    # Initialize database
    print("\n📊 Initializing database...")
    try:
        subprocess.check_call([sys.executable, "database/init_db.py"])
        print("✅ Database ready")
    except:
        print("⚠️  Database initialization skipped")
    
    # Test backend
    print("\n🧪 Testing setup...")
    try:
        # Quick import test
        sys.path.append(os.getcwd())
        from database.models import DatabaseManager
        from ai.ollama_client import OllamaClient
        
        db = DatabaseManager()
        ai = OllamaClient()
        
        print("✅ All components imported successfully")
        
    except Exception as e:
        print(f"⚠️  Component test warning: {e}")
    
    print("\n" + "="*50)
    print("🚀 SETUP COMPLETE!")
    print("="*50)
    print("\nTo start your demo:")
    print("1. python demo_script.py")
    print("   OR")
    print("2. python demo_script.py --quick")
    print("\n🏆 Good luck with D3CODE 2025!")

if __name__ == "__main__":
    setup_competition_ready()