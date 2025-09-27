"""
Analytics Database for Alpha Audit Pro
Tracks HCC analysis sessions and generates practice insights
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

class AnalyticsDB:
    def __init__(self, db_path="analytics.db"):
        self.db_path = db_path
        self.init_database()
        self.seed_sample_data()
    
    def init_database(self):
        """Initialize analytics database with comprehensive tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main analysis sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date DATE,
            physician_name TEXT,
            patient_id TEXT,
            visit_type TEXT,
            primary_diagnosis TEXT,
            clinical_notes_length INTEGER,
            total_suggestions INTEGER,
            top_hcc_category TEXT,
            top_icd_code TEXT,
            confidence_score REAL,
            priority_level TEXT,
            raf_value REAL,
            potential_revenue REAL,
            documentation_quality_score REAL,
            session_duration_seconds INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # HCC category tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hcc_category_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            hcc_category TEXT,
            category_name TEXT,
            occurrences INTEGER,
            total_raf_value REAL,
            total_revenue_impact REAL
        )
        """)
        
        # Provider performance tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provider_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            physician_name TEXT,
            total_analyses INTEGER,
            avg_confidence_score REAL,
            avg_documentation_quality REAL,
            total_revenue_identified REAL,
            avg_session_time REAL,
            high_priority_cases INTEGER
        )
        """)
        
        conn.commit()
        conn.close()
    
    def log_analysis_session(self, session_data: Dict[str, Any]):
        """Log a completed analysis session for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO analysis_sessions (
            session_date, physician_name, patient_id, visit_type, primary_diagnosis,
            clinical_notes_length, total_suggestions, top_hcc_category, top_icd_code,
            confidence_score, priority_level, raf_value, potential_revenue,
            documentation_quality_score, session_duration_seconds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get('session_date', datetime.now().date()),
            session_data.get('physician_name', 'Dr. Unknown'),
            session_data.get('patient_id', f'PT-{random.randint(1000, 9999)}'),
            session_data.get('visit_type', 'Follow-up'),
            session_data.get('primary_diagnosis', ''),
            session_data.get('clinical_notes_length', 0),
            session_data.get('total_suggestions', 0),
            session_data.get('top_hcc_category', ''),
            session_data.get('top_icd_code', ''),
            session_data.get('confidence_score', 0),
            session_data.get('priority_level', 'MEDIUM'),
            session_data.get('raf_value', 0),
            session_data.get('potential_revenue', 0),
            session_data.get('documentation_quality_score', 0),
            session_data.get('session_duration_seconds', 30)
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_analytics(self, target_date=None):
        """Get comprehensive daily analytics"""
        if not target_date:
            target_date = datetime.now().date()
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Daily summary
        cursor.execute("""
        SELECT 
            COUNT(*) as total_analyses,
            COUNT(DISTINCT physician_name) as active_physicians,
            AVG(confidence_score) as avg_confidence,
            AVG(documentation_quality_score) as avg_doc_quality,
            SUM(potential_revenue) as total_revenue_identified,
            COUNT(CASE WHEN priority_level = 'HIGH' THEN 1 END) as high_priority_cases
        FROM analysis_sessions 
        WHERE session_date = ?
        """, (target_date,))
        
        daily_summary = cursor.fetchone()
        
        # HCC category distribution for today
        cursor.execute("""
        SELECT top_hcc_category, COUNT(*) as count, SUM(potential_revenue) as revenue
        FROM analysis_sessions 
        WHERE session_date = ? AND top_hcc_category IS NOT NULL
        GROUP BY top_hcc_category
        ORDER BY count DESC
        """, (target_date,))
        
        hcc_distribution = cursor.fetchall()
        
        # Top conditions identified
        cursor.execute("""
        SELECT primary_diagnosis, COUNT(*) as frequency, AVG(confidence_score) as avg_confidence
        FROM analysis_sessions 
        WHERE session_date = ?
        GROUP BY primary_diagnosis
        ORDER BY frequency DESC
        LIMIT 10
        """, (target_date,))
        
        top_conditions = cursor.fetchall()
        
        conn.close()
        
        return {
            'daily_summary': daily_summary,
            'hcc_distribution': hcc_distribution,
            'top_conditions': top_conditions,
            'date': target_date
        }
    
    def get_monthly_trends(self, months_back=6):
        """Get monthly trending data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Monthly analysis volume and revenue
        cursor.execute("""
        SELECT 
            strftime('%Y-%m', session_date) as month,
            COUNT(*) as total_analyses,
            SUM(potential_revenue) as total_revenue,
            AVG(confidence_score) as avg_confidence,
            AVG(documentation_quality_score) as avg_doc_quality
        FROM analysis_sessions 
        WHERE session_date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', session_date)
        ORDER BY month
        """)
        
        monthly_trends = cursor.fetchall()
        
        conn.close()
        return monthly_trends
    
    def get_provider_performance(self, time_period='week'):
        """Get provider performance comparison"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if time_period == 'week':
            date_filter = "session_date >= date('now', '-7 days')"
        elif time_period == 'month':
            date_filter = "session_date >= date('now', '-30 days')"
        else:
            date_filter = "session_date >= date('now', '-7 days')"
        
        cursor.execute(f"""
        SELECT 
            physician_name,
            COUNT(*) as total_analyses,
            AVG(confidence_score) as avg_confidence,
            AVG(documentation_quality_score) as avg_doc_quality,
            SUM(potential_revenue) as total_revenue,
            COUNT(CASE WHEN priority_level = 'HIGH' THEN 1 END) as high_priority_cases
        FROM analysis_sessions 
        WHERE {date_filter}
        GROUP BY physician_name
        ORDER BY total_analyses DESC
        """)
        
        provider_stats = cursor.fetchall()
        
        conn.close()
        return provider_stats
    
    def seed_sample_data(self):
        """Generate realistic sample data for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample physicians
        physicians = [
            "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Davis", 
            "Dr. Robert Wilson", "Dr. Lisa Garcia", "Dr. David Miller"
        ]
        
        # Sample conditions with their typical HCC mappings
        conditions_data = [
            ("Type 2 diabetes mellitus", "HCC 19", "E11.9", 0.104, 1768, "MEDIUM"),
            ("Chronic kidney disease", "HCC 138", "N18.3", 0.287, 4879, "HIGH"),
            ("Heart failure", "HCC 85", "I50.9", 0.323, 5491, "HIGH"),
            ("COPD exacerbation", "HCC 111", "J44.1", 0.328, 5576, "HIGH"),
            ("Major depression", "HCC 155", "F32.1", 0.309, 5253, "MEDIUM"),
            ("Hypertension", "HCC 0", "I10", 0.0, 0, "LOW"),
            ("Diabetic nephropathy", "HCC 18", "E11.22", 0.302, 5134, "HIGH"),
            ("Atrial fibrillation", "HCC 96", "I48.91", 0.244, 4148, "MEDIUM"),
            ("Chronic liver disease", "HCC 27", "K72.90", 0.194, 3298, "MEDIUM"),
            ("Peripheral artery disease", "HCC 109", "I73.9", 0.224, 3808, "MEDIUM")
        ]
        
        visit_types = ["Emergency Visit", "Follow-Up Visit", "Annual Wellness Visit", 
                      "Hospital Admission", "Consultation", "Preventive Care"]
        
        # Generate data for last 90 days
        for days_ago in range(90):
            session_date = datetime.now().date() - timedelta(days=days_ago)
            
            # Generate 5-15 sessions per day
            daily_sessions = random.randint(5, 15)
            
            for _ in range(daily_sessions):
                physician = random.choice(physicians)
                condition_data = random.choice(conditions_data)
                visit_type = random.choice(visit_types)
                
                # Add some randomness to confidence and documentation quality
                base_confidence = random.uniform(55, 90)
                base_doc_quality = random.uniform(60, 95)
                
                session_data = {
                    'session_date': session_date,
                    'physician_name': physician,
                    'patient_id': f'PT-{random.randint(10000, 99999)}',
                    'visit_type': visit_type,
                    'primary_diagnosis': condition_data[0],
                    'clinical_notes_length': random.randint(50, 300),
                    'total_suggestions': random.randint(1, 5),
                    'top_hcc_category': condition_data[1],
                    'top_icd_code': condition_data[2],
                    'confidence_score': round(base_confidence, 1),
                    'priority_level': condition_data[5],
                    'raf_value': condition_data[3],
                    'potential_revenue': condition_data[4],
                    'documentation_quality_score': round(base_doc_quality, 1),
                    'session_duration_seconds': random.randint(20, 180)
                }
                
                self.log_analysis_session(session_data)
        
        conn.close()
        print("Sample analytics data generated successfully!")

# Usage example
if __name__ == "__main__":
    analytics = AnalyticsDB()
    
    # Get today's analytics
    daily_data = analytics.get_daily_analytics()
    print("Daily Analytics:", daily_data)
    
    # Get monthly trends
    monthly_data = analytics.get_monthly_trends()
    print("Monthly Trends:", monthly_data)