from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
import os
import time
import random
import requests
import json
from datetime import datetime

app = FastAPI(title="HCC Coding Assistant API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class AnalysisRequest(BaseModel):
    clinical_notes: str
    visit_type: str
    primary_diagnosis: str
    provider_name: Optional[str] = "Dr. Provider"
    # NEW: Essential Demographics for HCC Risk Calculation
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    patient_medical_history: Optional[str] = ""
    current_medications: Optional[str] = ""
    lab_values: Optional[str] = ""
    # Legacy support
    patient_history: Optional[str] = None
    current_icd: Optional[str] = None

class PhysicianInput(BaseModel):
    primary_diagnosis: str
    clinical_notes: str
    current_icd: Optional[str] = None
    patient_history: Optional[str] = None

class ICDSuggestion(BaseModel):
    icd_code: str
    description: str
    hcc_code: Optional[str]
    hcc_description: Optional[str]
    raf_weight: float
    confidence_score: float
    reasoning: str
    priority_level: Optional[str] = "MEDIUM"
    priority_explanation: Optional[str] = "Standard clinical priority"
    # NEW: Enhanced fields for ICD-10 selection guidance
    supporting_text: Optional[str] = ""
    demographic_risk_factor: Optional[float] = 1.0
    ai_confidence: Optional[float] = 0.0
    # NEW: Revenue impact comparison
    annual_revenue_impact: int = 0
    is_hcc_eligible: bool = False
    suggested_use_case: str = ""
    alternative_codes: Optional[List[str]] = []

class HCCAnalysisResponse(BaseModel):
    suggestions: List[ICDSuggestion]
    extracted_conditions: Dict
    total_raf_impact: float
    recommendations: List[str]
    ai_available: bool
    # NEW: Enhanced response fields for ICD-10 guidance
    overall_confidence: str
    priority_level: str
    potential_revenue_impact: str
    demographic_analysis: Dict
    action_items: List[str]
    additional_documentation: List[str]
    # NEW: ICD-10 selection guidance
    hcc_vs_non_hcc_comparison: Dict
    top_revenue_opportunities: List[str]
    documentation_improvement_tips: List[str]

# OLLAMA AI Integration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3"  # Microsoft Phi3 - Excellent for medical analysis, faster and lighter than Llama 3.1

def check_ollama_availability():
    """Check if OLLAMA is running and available"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_with_ollama(clinical_data: Dict) -> Dict:
    """Use OLLAMA AI for intelligent medical analysis"""
    try:
        # Construct comprehensive prompt for medical analysis
        prompt = f"""
You are an expert HCC (Hierarchical Condition Category) coding specialist and clinical analyst. 

PATIENT PROFILE:
- Age: {clinical_data.get('age', 'Unknown')}
- Gender: {clinical_data.get('gender', 'Unknown')}
- Visit Type: {clinical_data.get('visit_type', 'Unknown')}

PRIMARY DIAGNOSIS: {clinical_data.get('primary_diagnosis', '')}

CLINICAL DOCUMENTATION:
{clinical_data.get('clinical_notes', '')}

MEDICAL HISTORY: {clinical_data.get('medical_history', 'None provided')}

MEDICATIONS: {clinical_data.get('medications', 'None provided')}

LAB VALUES: {clinical_data.get('lab_values', 'None provided')}

Based on this comprehensive clinical picture, provide a detailed analysis focusing on:

1. **RISK STRATIFICATION**: How do the patient's age and gender affect HCC risk? 
2. **CONDITION SEVERITY**: Assess the severity and specificity of documented conditions
3. **HCC OPPORTUNITIES**: Identify potential HCC categories with high confidence
4. **DOCUMENTATION GAPS**: What additional documentation would strengthen HCC capture?
5. **DEMOGRAPHIC IMPACT**: How do demographics change the risk profile?

Respond in JSON format:
{
    "primary_conditions": ["list of main conditions identified"],
    "hcc_opportunities": [
        {
            "condition": "condition name",
            "hcc_category": "HCC XX",
            "confidence": 0.85,
            "demographic_risk": 1.2,
            "reasoning": "detailed clinical reasoning"
        }
    ],
    "risk_factors": {
        "age_impact": "high/medium/low",
        "gender_considerations": "relevant factors",
        "comorbidity_risk": "assessment"
    },
    "documentation_recommendations": ["specific suggestions"],
    "overall_assessment": "comprehensive summary"
}
"""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            ai_response = response.json()
            try:
                # Parse the AI response
                ai_analysis = json.loads(ai_response.get('response', '{}'))
                return {
                    'success': True,
                    'analysis': ai_analysis,
                    'raw_response': ai_response.get('response', '')
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Failed to parse AI response as JSON',
                    'raw_response': ai_response.get('response', '')
                }
        else:
            return {'success': False, 'error': f'OLLAMA API error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'OLLAMA connection failed: {str(e)}'}

def calculate_demographic_risk_multiplier(age: int, gender: str, conditions: List[str]) -> float:
    """Calculate risk multiplier based on demographics and conditions"""
    multiplier = 1.0
    
    # Age-based risk adjustment (critical for HCC)
    if age >= 85:
        multiplier += 0.8  # Very high risk
    elif age >= 75:
        multiplier += 0.6  # High risk
    elif age >= 65:
        multiplier += 0.4  # Medicare age, higher risk
    elif age >= 50:
        multiplier += 0.2  # Moderate risk increase
    elif age < 30:
        multiplier -= 0.3  # Lower risk for young patients
    
    # Gender-specific risk factors
    if gender and gender.lower() in ['female', 'f']:
        # Gender-specific conditions
        heart_conditions = ['heart', 'cardiac', 'coronary', 'myocardial']
        if any(condition in ' '.join(conditions).lower() for condition in heart_conditions):
            if age >= 65:
                multiplier += 0.1  # Higher heart disease risk in older women
    elif gender and gender.lower() in ['male', 'm']:
        # Men typically have higher cardiovascular risk at younger ages
        if age >= 45:
            multiplier += 0.1
    
    # Condition-specific demographic adjustments
    condition_text = ' '.join(conditions).lower()
    
    # Diabetes risk increases significantly with age
    if 'diabetes' in condition_text or 'diabetic' in condition_text:
        if age >= 60:
            multiplier += 0.2
    
    # Heart conditions are more serious in older patients
    if any(term in condition_text for term in ['heart', 'cardiac', 'coronary']):
        if age >= 70:
            multiplier += 0.3
        elif age >= 50:
            multiplier += 0.1
    
    # Kidney disease progression accelerates with age
    if 'kidney' in condition_text or 'renal' in condition_text:
        if age >= 65:
            multiplier += 0.25
    
    return round(min(3.0, max(0.3, multiplier)), 2)  # Cap between 0.3 and 3.0

# Simple database functions
def init_simple_db():
    """Initialize a simple database if it doesn't exist"""
    db_path = "simple_hcc.db"
    
    # Force regeneration for updated data - remove this line after first run
    if os.path.exists(db_path):
        os.remove(db_path)
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
        # Enhanced sample data with comprehensive ICD-10 coverage
        # Format: (ICD Code, Description, HCC Category or None, RAF Value, Annual Impact)
        sample_data = [
            # DIABETES CONDITIONS - Show HCC vs Non-HCC options
            # Non-HCC diabetes codes (doctors often use these by mistake)
            ("E11.9", "Type 2 diabetes mellitus without complications", "No HCC", 0.0, 0),
            ("E10.9", "Type 1 diabetes mellitus without complications", "No HCC", 0.0, 0),
            
            # HCC-eligible diabetes codes (doctors should use these instead)
            ("E11.22", "Type 2 diabetes mellitus with diabetic chronic kidney disease", "HCC 18", 0.302, 5134),
            ("E11.51", "Type 2 diabetes mellitus with diabetic peripheral angiopathy without gangrene", "HCC 18", 0.302, 5134),
            ("E11.52", "Type 2 diabetes mellitus with diabetic peripheral angiopathy with gangrene", "HCC 18", 0.302, 5134),
            ("E11.40", "Type 2 diabetes mellitus with diabetic neuropathy, unspecified", "HCC 18", 0.302, 5134),
            ("E11.65", "Type 2 diabetes mellitus with hyperglycemia", "HCC 19", 0.104, 1768),
            ("E11.319", "Type 2 diabetes mellitus with unspecified diabetic retinopathy without macular edema", "HCC 18", 0.302, 5134),
            
            # HEART CONDITIONS - Critical for revenue capture
            # Basic heart codes (lower value)
            ("I25.9", "Chronic ischemic heart disease, unspecified", "HCC 86", 0.273, 4641),
            ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris", "HCC 86", 0.273, 4641),
            
            # High-value heart failure codes (doctors should prioritize these)
            ("I50.9", "Heart failure, unspecified", "HCC 85", 0.323, 5491),
            ("I50.1", "Left ventricular failure, unspecified", "HCC 85", 0.323, 5491),
            ("I50.20", "Unspecified systolic (congestive) heart failure", "HCC 85", 0.323, 5491),
            ("I50.22", "Chronic systolic (congestive) heart failure", "HCC 85", 0.323, 5491),
            ("I50.30", "Unspecified diastolic (congestive) heart failure", "HCC 85", 0.323, 5491),
            ("I50.32", "Chronic diastolic (congestive) heart failure", "HCC 85", 0.323, 5491),
            ("I50.40", "Unspecified combined systolic and diastolic heart failure", "HCC 85", 0.323, 5491),
            ("I11.0", "Hypertensive heart disease with heart failure", "HCC 85", 0.323, 5491),
            
            # Heart attack codes
            ("I21.9", "Acute myocardial infarction, unspecified", "HCC 86", 0.273, 4641),
            ("I25.2", "Old myocardial infarction", "HCC 86", 0.273, 4641),
            ("I21.01", "ST elevation (STEMI) myocardial infarction involving left main coronary artery", "HCC 86", 0.273, 4641),
            
            # KIDNEY CONDITIONS - High RAF values
            # Non-HCC kidney codes
            ("N28.9", "Disorder of kidney and ureter, unspecified", "No HCC", 0.0, 0),
            
            # HCC kidney codes (much higher value)
            ("N18.1", "Chronic kidney disease, stage 1", "HCC 139", 0.000, 0),  # Stage 1 has no RAF
            ("N18.2", "Chronic kidney disease, stage 2 (mild)", "HCC 139", 0.000, 0),  # Stage 2 has no RAF
            ("N18.3", "Chronic kidney disease, stage 3 (moderate)", "HCC 138", 0.287, 4879),
            ("N18.4", "Chronic kidney disease, stage 4 (severe)", "HCC 137", 0.398, 6766),
            ("N18.5", "Chronic kidney disease, stage 5 (severe)", "HCC 136", 0.675, 11475),
            ("N18.6", "End stage renal disease", "HCC 134", 0.675, 11475),
            ("Z94.0", "Kidney transplant status", "HCC 134", 0.525, 8925),
            ("Z99.2", "Dependence on renal dialysis", "HCC 134", 0.525, 8925),
            
            # MENTAL HEALTH CONDITIONS
            # Basic depression (lower value)
            ("F32.9", "Major depressive disorder, single episode, unspecified", "HCC 155", 0.309, 5253),
            ("F32.1", "Major depressive disorder, single episode, moderate", "HCC 155", 0.309, 5253),
            ("F32.2", "Major depressive disorder, single episode, severe without psychotic features", "HCC 154", 0.331, 5627),
            
            # Recurrent depression (higher value)
            ("F33.1", "Major depressive disorder, recurrent, moderate", "HCC 155", 0.309, 5253),
            ("F33.2", "Major depressive disorder, recurrent severe without psychotic features", "HCC 154", 0.331, 5627),
            
            # RESPIRATORY CONDITIONS  
            ("J44.0", "Chronic obstructive pulmonary disease with acute lower respiratory infection", "HCC 111", 0.328, 5576),
            ("J44.1", "Chronic obstructive pulmonary disease with (acute) exacerbation", "HCC 111", 0.328, 5576),
            
            # CANCER CONDITIONS (very high RAF)
            ("C78.00", "Secondary malignant neoplasm of unspecified lung", "HCC 8", 0.677, 11509),
            ("C25.9", "Malignant neoplasm of pancreas, unspecified", "HCC 8", 0.677, 11509),
            
            # STROKE CONDITIONS
            ("I63.9", "Cerebral infarction, unspecified", "HCC 100", 0.350, 5950),
            ("G93.1", "Anoxic brain damage, not elsewhere classified", "HCC 100", 0.350, 5950),
            
            # LIVER CONDITIONS
            ("K72.90", "Hepatic failure, unspecified without coma", "HCC 27", 0.675, 11475),
            ("K70.30", "Alcoholic cirrhosis of liver without ascites", "HCC 27", 0.675, 11475),
            
            # SUBSTANCE ABUSE
            ("F10.20", "Alcohol dependence, uncomplicated", "HCC 54", 0.328, 5576),
            ("F11.20", "Opioid dependence, uncomplicated", "HCC 54", 0.328, 5576)
        ]
        
        cursor.executemany("""
        INSERT INTO hcc_mappings (icd_code, description, hcc_category, raf_value, annual_impact)
        VALUES (?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
        conn.close()

def search_hcc_codes(keywords: List[str]) -> List[Dict]:
    """Enhanced search for HCC codes with better matching"""
    init_simple_db()
    
    conn = sqlite3.connect("simple_hcc.db")
    cursor = conn.cursor()
    
    # Build prioritized search queries
    all_results = []
    
    # Priority 1: Exact condition matches
    priority_mappings = {
        'heart': ['heart', 'cardiac', 'coronary', 'myocardial', 'ischemic'],
        'diabetes': ['diabetes', 'diabetic'],
        'kidney': ['kidney', 'renal', 'nephropathy'],
        'failure': ['failure']
    }
    
    for keyword in keywords[:5]:  # Check more keywords
        keyword_lower = keyword.lower()
        
        # Find the primary condition category
        primary_condition = None
        for condition, synonyms in priority_mappings.items():
            if any(syn in keyword_lower for syn in synonyms):
                primary_condition = condition
                break
        
        if primary_condition:
            # Build targeted query for this condition
            if primary_condition == 'heart':
                query = """SELECT * FROM hcc_mappings WHERE 
                          (description LIKE '%heart%' OR description LIKE '%cardiac%' OR 
                           description LIKE '%coronary%' OR description LIKE '%myocardial%' OR
                           description LIKE '%ischemic%' OR icd_code LIKE 'I%')
                          ORDER BY raf_value DESC"""
            elif primary_condition == 'diabetes':
                query = """SELECT * FROM hcc_mappings WHERE 
                          (description LIKE '%diabetes%' OR description LIKE '%diabetic%' OR
                           icd_code LIKE 'E1%')
                          ORDER BY raf_value DESC"""
            elif primary_condition == 'kidney':
                query = """SELECT * FROM hcc_mappings WHERE 
                          (description LIKE '%kidney%' OR description LIKE '%renal%' OR
                           description LIKE '%nephropathy%' OR icd_code LIKE 'N18%')
                          ORDER BY raf_value DESC"""
            else:
                # Generic search
                query = "SELECT * FROM hcc_mappings WHERE description LIKE ? ORDER BY raf_value DESC"
                cursor.execute(query, [f"%{keyword}%"])
                results = cursor.fetchall()
        else:
            # Fallback: broad search
            query = "SELECT * FROM hcc_mappings WHERE (description LIKE ? OR icd_code LIKE ?) ORDER BY raf_value DESC"
            cursor.execute(query, [f"%{keyword}%", f"%{keyword}%"])
            results = cursor.fetchall()
        
        if primary_condition in ['heart', 'diabetes', 'kidney']:
            cursor.execute(query)
            results = cursor.fetchall()
        
        # Convert results and add to collection
        for row in results:
            mapping = {
                'icd_code': row[1],
                'description': row[2],
                'hcc_category': row[3],
                'raf_value': row[4],
                'annual_impact': row[5],
                'relevance_score': 100 if primary_condition else 50  # Priority scoring
            }
            
            # Avoid duplicates
            if not any(m['icd_code'] == mapping['icd_code'] for m in all_results):
                all_results.append(mapping)
    
    # Sort by relevance score then RAF value
    all_results.sort(key=lambda x: (x.get('relevance_score', 0), x['raf_value']), reverse=True)
    
    conn.close()
    return all_results[:8]  # Return top 8 results

def extract_medical_keywords(text: str) -> Dict:
    """Enhanced medical keyword extraction with proper condition mapping"""
    keywords = []
    
    # Comprehensive medical terms with proper categorization
    medical_terms = {
        # Heart conditions
        'heart': ['heart', 'cardiac', 'coronary', 'myocardial', 'cardiovascular', 'ischemic heart'],
        'heart failure': ['heart failure', 'congestive heart failure', 'chf', 'heart failure'],
        'myocardial': ['myocardial', 'heart attack', 'mi', 'coronary artery'],
        
        # Kidney conditions
        'kidney': ['kidney', 'renal', 'nephropathy', 'chronic kidney disease', 'ckd'],
        'dialysis': ['dialysis', 'hemodialysis', 'peritoneal dialysis'],
        
        # Diabetes
        'diabetes': ['diabetes', 'diabetic', 'dm', 'blood sugar', 'glucose', 'hyperglycemia', 'hba1c'],
        'diabetic complications': ['diabetic nephropathy', 'diabetic retinopathy', 'diabetic neuropathy'],
        
        # General medical terms
        'chronic': ['chronic', 'long-term', 'ongoing'],
        'acute': ['acute', 'sudden', 'emergency'],
        'severe': ['severe', 'critical', 'advanced'],
        'moderate': ['moderate', 'mild', 'stable']
    }
    
    text_lower = text.lower()
    
    # Find the most specific matches first
    primary_condition = None
    condition_keywords = []
    
    for condition_category, terms in medical_terms.items():
        for term in terms:
            if term in text_lower:
                condition_keywords.append(term)
                if not primary_condition and condition_category in ['heart', 'heart failure', 'kidney', 'diabetes']:
                    primary_condition = condition_category
    
    # If we found specific condition keywords, use those
    if condition_keywords:
        keywords = list(set(condition_keywords))  # Remove duplicates
    else:
        # Fallback to basic extraction
        basic_terms = ['diabetes', 'heart', 'kidney', 'failure', 'chronic', 'acute']
        for term in basic_terms:
            if term in text_lower:
                keywords.append(term)
    
    # Determine characteristics
    chronicity = 'chronic' if any(term in text_lower for term in ['chronic', 'long-term', 'ongoing']) else 'acute'
    severity = 'severe' if any(term in text_lower for term in ['severe', 'critical', 'advanced']) else \
               'moderate' if any(term in text_lower for term in ['moderate', 'stable']) else 'mild'
    
    # Extract primary condition based on detected keywords
    primary_condition = 'unknown'
    if primary_condition:
        primary_condition = primary_condition
    elif any(term in keywords for term in ['diabetes', 'diabetic', 'dm']):
        primary_condition = 'diabetes'
    elif any(term in keywords for term in ['heart', 'cardiac', 'coronary', 'myocardial']):
        primary_condition = 'heart condition'
    elif any(term in keywords for term in ['kidney', 'renal', 'nephropathy']):
        primary_condition = 'kidney disease'
    
    return {
        'medical_keywords': keywords,
        'extracted_terms': keywords,
        'chronicity': chronicity,
        'severity': severity,
        'primary_condition': primary_condition,
        'secondary_conditions': keywords[1:3] if len(keywords) > 1 else []
    }

@app.get("/")
async def root():
    return {
        "message": "HCC Coding Assistant API",
        "version": "1.0.0",
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    ai_status = check_ollama_availability()
    return {
        "status": "healthy",
        "ai_available": ai_status,
        "ai_model": OLLAMA_MODEL if ai_status else "Not available",
        "database_ready": True,
        "ollama_url": OLLAMA_BASE_URL
    }

@app.post("/analyze", response_model=HCCAnalysisResponse)
async def analyze_notes_intelligently(data: AnalysisRequest):
    """Enhanced AI-powered analysis with demographics and OLLAMA integration"""
    
    try:
        start_time = time.time()
        
        # Check AI availability
        ai_available = check_ollama_availability()
        
        # Prepare comprehensive clinical data for analysis
        clinical_data = {
            'age': data.patient_age,
            'gender': data.patient_gender,
            'visit_type': data.visit_type,
            'primary_diagnosis': data.primary_diagnosis,
            'clinical_notes': data.clinical_notes,
            'medical_history': data.patient_medical_history or data.patient_history or "",
            'medications': data.current_medications,
            'lab_values': data.lab_values
        }
        
        # Initialize response components
        suggestions = []
        ai_analysis = None
        demographic_analysis = {}
        additional_documentation = []  # Initialize the missing variable
        
        # AI Analysis (if available)
        if ai_available:
            print("[AI] Using OLLAMA AI for analysis...")
            ai_result = analyze_with_ollama(clinical_data)
            if ai_result['success']:
                ai_analysis = ai_result['analysis']
                print(f"[SUCCESS] AI Analysis successful: {ai_analysis}")
            else:
                print(f"[ERROR] AI Analysis failed: {ai_result['error']}")
                ai_available = False
        
        # Fallback to enhanced rule-based analysis
        if not ai_available or not ai_analysis:
            print("[ANALYSIS] Using enhanced rule-based analysis...")
            
        # Extract medical conditions (enhanced with demographics)
        full_text = f"{data.primary_diagnosis} {data.clinical_notes}"
        if data.patient_medical_history:
            full_text += f" {data.patient_medical_history}"
        
        extracted_conditions = extract_medical_keywords(full_text)
        
        # Search for relevant HCC codes
        search_keywords = extracted_conditions.get('medical_keywords', [])
        search_keywords.append(data.primary_diagnosis.lower())
        unique_keywords = list(set(search_keywords))
        mappings = search_hcc_codes(unique_keywords)
        
        # Calculate demographic risk multiplier
        demographic_multiplier = 1.0
        if data.patient_age and data.patient_gender:
            demographic_multiplier = calculate_demographic_risk_multiplier(
                data.patient_age, 
                data.patient_gender, 
                search_keywords
            )
            
            demographic_analysis = {
                'age_group': 'Senior (65+)' if data.patient_age >= 65 else 'Adult (18-64)' if data.patient_age >= 18 else 'Youth (<18)',
                'risk_multiplier': demographic_multiplier,
                'age_impact': 'High' if data.patient_age >= 70 else 'Moderate' if data.patient_age >= 50 else 'Low',
                'gender_considerations': f"{data.patient_gender} - age {data.patient_age}"
            }
        
        # Process each mapping with AI enhancement
        for i, mapping in enumerate(mappings[:10]):
            # Base confidence calculation
            confidence_factors = {
                'keyword_match': 0,
                'clinical_specificity': 0,
                'documentation_quality': 0,
                'condition_clarity': 0,
                'ai_enhancement': 0,
                'demographic_relevance': 0
            }
            
            # Enhanced keyword matching
            icd_keywords = mapping['description'].lower().split()
            matched_keywords = sum(1 for word in icd_keywords if word in full_text.lower())
            if len(icd_keywords) > 0:
                confidence_factors['keyword_match'] = (matched_keywords / len(icd_keywords)) * 30
            
            # Clinical specificity
            specificity_terms = ['chronic', 'acute', 'severe', 'moderate', 'stage', 'type', 'with', 'ejection fraction', 'bnp', 'creatinine']
            specificity_score = sum(1 for term in specificity_terms if term in full_text.lower())
            confidence_factors['clinical_specificity'] = min(25, specificity_score * 5)
            
            # Documentation quality
            documentation_terms = ['patient', 'history', 'examination', 'assessment', 'plan', 'monitor', 'treatment', 'medication', 'lab', 'vital']
            doc_score = sum(1 for term in documentation_terms if term in full_text.lower())
            confidence_factors['documentation_quality'] = min(20, doc_score * 2)
            
            # Condition clarity
            if data.primary_diagnosis.lower() in mapping['description'].lower():
                confidence_factors['condition_clarity'] = 15
            
            # AI enhancement (if AI analysis is available)
            ai_confidence_boost = 0
            if ai_analysis and 'hcc_opportunities' in ai_analysis:
                for ai_opp in ai_analysis['hcc_opportunities']:
                    if mapping['hcc_category'].replace('HCC ', '') in ai_opp.get('hcc_category', ''):
                        ai_confidence_boost = ai_opp.get('confidence', 0) * 20
                        confidence_factors['ai_enhancement'] = ai_confidence_boost
                        break
            
            # Demographic relevance
            if demographic_multiplier > 1.2:
                confidence_factors['demographic_relevance'] = 10
            elif demographic_multiplier > 1.0:
                confidence_factors['demographic_relevance'] = 5
            
            # Calculate final confidence
            total_confidence = sum(confidence_factors.values())
            base_confidence = min(95, max(35, total_confidence))
            
            # Apply demographic adjustment to confidence
            final_confidence = base_confidence * min(1.3, demographic_multiplier)
            final_confidence = min(95, max(40, final_confidence))
            
            # Enhanced priority scoring with demographics
            priority_score = 0
            raf_value = mapping['raf_value']
            
            # RAF-based priority (enhanced)
            if raf_value > 0.4:
                priority_score += 35
            elif raf_value > 0.2:
                priority_score += 20
            else:
                priority_score += 10
            
            # Demographic priority boost
            if data.patient_age and data.patient_age >= 65:
                priority_score += 15  # Medicare patients are higher priority
            if demographic_multiplier > 1.5:
                priority_score += 10  # High-risk demographics
            
            # Clinical urgency
            urgent_terms = ['severe', 'acute', 'emergency', 'critical', 'advanced', 'reduced ejection fraction', 'stage 4', 'stage 5']
            if any(term in full_text.lower() for term in urgent_terms):
                priority_score += 25
            
            # AI priority enhancement
            if ai_analysis and 'risk_factors' in ai_analysis:
                risk_assessment = ai_analysis['risk_factors']
                if risk_assessment.get('age_impact') == 'high':
                    priority_score += 15
                if 'high' in str(risk_assessment.get('comorbidity_risk', '')).lower():
                    priority_score += 10
            
            # Determine priority level
            if priority_score > 80:
                priority_level = "HIGH"
                priority_explanation = f"Critical: High RAF ({raf_value}), age {data.patient_age}, significant clinical factors"
            elif priority_score > 50:
                priority_level = "MEDIUM"
                priority_explanation = f"Important: Moderate RAF ({raf_value}), demographic risk factor {demographic_multiplier}"
            else:
                priority_level = "LOW"
                priority_explanation = f"Review: Lower RAF ({raf_value}), verify coding accuracy"
            
            # Enhanced reasoning with AI insights
            reasoning_parts = []
            
            if ai_analysis:
                # Use AI reasoning if available
                for ai_opp in ai_analysis.get('hcc_opportunities', []):
                    if mapping['hcc_category'].replace('HCC ', '') in ai_opp.get('hcc_category', ''):
                        reasoning_parts.append(f"AI Analysis: {ai_opp.get('reasoning', '')}")
                        break
            
            if final_confidence > 80:
                reasoning_parts.append(f"Strong clinical correlation with {mapping['description']}")
            elif final_confidence > 60:
                reasoning_parts.append(f"Good match for {mapping['description']}")
            else:
                reasoning_parts.append(f"Potential match requires clinical review")
            
            if demographic_multiplier > 1.2:
                reasoning_parts.append(f"Demographic risk factors increase relevance (factor: {demographic_multiplier})")
            
            reasoning = ". ".join(reasoning_parts) + f". {priority_explanation}."
            
            # Find supporting text from clinical notes
            supporting_text = ""
            for keyword in icd_keywords[:3]:
                if keyword in full_text.lower():
                    # Find sentence containing the keyword
                    sentences = full_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            supporting_text = sentence.strip()
                            break
                    if supporting_text:
                        break
            
            # Calculate adjusted RAF value with demographics
            adjusted_raf = raf_value * demographic_multiplier
            
            # Determine if this is HCC-eligible
            is_hcc_eligible = mapping['hcc_category'] != "No HCC" and raf_value > 0
            annual_revenue = int(adjusted_raf * 17000) if is_hcc_eligible else 0
            
            # Generate suggested use case based on condition
            suggested_use_case = ""
            if "diabetes" in mapping['description'].lower():
                if "kidney" in mapping['description'].lower():
                    suggested_use_case = "Use when patient has diabetes WITH kidney involvement/nephropathy"
                elif "neuropathy" in mapping['description'].lower():
                    suggested_use_case = "Use when patient has diabetes WITH nerve damage/neuropathy"
                elif "without complications" in mapping['description'].lower():
                    suggested_use_case = "WARNING: AVOID - Use more specific codes if complications exist"
                else:
                    suggested_use_case = "Use for diabetes with documented complications"
            elif "heart" in mapping['description'].lower():
                if "failure" in mapping['description'].lower():
                    suggested_use_case = "Use when patient has documented heart failure (higher RAF value)"
                else:
                    suggested_use_case = "Use for coronary artery disease without heart failure"
            elif "kidney" in mapping['description'].lower():
                if "stage" in mapping['description'].lower():
                    suggested_use_case = "Use when CKD stage is documented (higher stages = higher RAF)"
                else:
                    suggested_use_case = "Use for general kidney disorders"
            
            # Find alternative codes for comparison
            alternative_codes = []
            if not is_hcc_eligible:
                # For non-HCC codes, suggest HCC alternatives
                for alt_mapping in mappings:
                    if (alt_mapping['hcc_category'] != "No HCC" and 
                        any(word in alt_mapping['description'].lower() for word in mapping['description'].lower().split()[:3])):
                        alternative_codes.append(f"{alt_mapping['icd_code']} ({alt_mapping['hcc_category']}, +${int(alt_mapping['raf_value'] * 17000):,})")
                        if len(alternative_codes) >= 2:
                            break
            
            suggestion = ICDSuggestion(
                icd_code=mapping['icd_code'],
                description=mapping['description'],
                hcc_code=mapping['hcc_category'],
                hcc_description=mapping['hcc_category'],
                raf_weight=round(adjusted_raf, 3),
                confidence_score=round(final_confidence, 1),
                reasoning=reasoning,
                priority_level=priority_level,
                priority_explanation=priority_explanation,
                supporting_text=supporting_text or "Clinical documentation supports this condition",
                demographic_risk_factor=demographic_multiplier,
                ai_confidence=ai_confidence_boost / 20 if ai_confidence_boost > 0 else 0.0,
                # NEW: ICD-10 selection guidance fields
                annual_revenue_impact=annual_revenue,
                is_hcc_eligible=is_hcc_eligible,
                suggested_use_case=suggested_use_case,
                alternative_codes=alternative_codes
            )
            
            suggestions.append(suggestion)
        
        # Sort by confidence and priority
        def sort_key(s):
            priority_weight = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            return (priority_weight.get(s.priority_level, 1), s.confidence_score, s.raf_weight)
        
        suggestions.sort(key=sort_key, reverse=True)
        
        # Generate ICD-10 comparison analysis
        hcc_codes = [s for s in suggestions if s.is_hcc_eligible]
        non_hcc_codes = [s for s in suggestions if not s.is_hcc_eligible]
        
        hcc_vs_non_hcc_comparison = {
            "hcc_eligible_count": len(hcc_codes),
            "non_hcc_count": len(non_hcc_codes),
            "potential_missed_revenue": sum(s.annual_revenue_impact for s in hcc_codes),
            "hcc_average_raf": round(sum(s.raf_weight for s in hcc_codes) / len(hcc_codes), 3) if hcc_codes else 0,
            "top_revenue_codes": [f"{s.icd_code}: +${s.annual_revenue_impact:,}" for s in sorted(hcc_codes, key=lambda x: x.annual_revenue_impact, reverse=True)[:3]]
        }
        
        # Generate top revenue opportunities
        top_revenue_opportunities = []
        for suggestion in sorted(suggestions, key=lambda x: x.annual_revenue_impact, reverse=True)[:5]:
            if suggestion.is_hcc_eligible:
                top_revenue_opportunities.append(
                    f"{suggestion.icd_code} ({suggestion.hcc_code}): +${suggestion.annual_revenue_impact:,}/year - {suggestion.suggested_use_case}"
                )
        
        # Generate documentation improvement tips
        documentation_improvement_tips = [
            "Document SPECIFIC complications: Instead of 'diabetes', use 'diabetes with kidney disease'",
            "Include SEVERITY levels: Stage of kidney disease, ejection fraction for heart failure",
            "Note CHRONIC vs ACUTE: Chronic conditions often have higher HCC values",
            "Capture COMORBIDITIES: Multiple conditions can increase overall RAF score"
        ]
        
        if data.patient_age and data.patient_age >= 65:
            documentation_improvement_tips.append(
                "MEDICARE FOCUS: Ensure annual recapture of all chronic conditions for this Medicare patient"
            )
        
        # Update recommendations to focus on ICD-10 selection
        recommendations = []
        if suggestions:
            top = suggestions[0]
            if top.is_hcc_eligible:
                recommendations.append(f"RECOMMENDED ICD-10: {top.icd_code} ({top.hcc_code}) - Revenue: +${top.annual_revenue_impact:,}/year")
            else:
                recommendations.append(f"CURRENT SELECTION: {top.icd_code} (No HCC) - Consider HCC-eligible alternatives")
                if top.alternative_codes:
                    recommendations.append(f"BETTER OPTIONS: {', '.join(top.alternative_codes[:2])}")
        
        if data.patient_age and data.patient_age >= 65:
            recommendations.append("[MEDICARE] MEDICARE PATIENT: Ensure annual HCC recapture for continued risk adjustment")
        
        if demographic_multiplier > 1.3:
            recommendations.append(f"[WARNING] HIGH DEMOGRAPHIC RISK: Age/gender profile increases clinical significance (factor: {demographic_multiplier})")
        
        # AI-powered recommendations
        if ai_analysis:
            if 'documentation_recommendations' in ai_analysis:
                additional_documentation.extend(ai_analysis['documentation_recommendations'])
            
            if 'overall_assessment' in ai_analysis:
                recommendations.append(f"[AI INSIGHT] {ai_analysis['overall_assessment']}")
        
        # Enhanced action items focused on ICD-10 selection
        action_items = [
            "Review suggested ICD-10 codes for HCC eligibility before final selection",
            "Compare revenue impact of different ICD-10 code options", 
            "Verify clinical documentation supports the most specific ICD-10 code available",
            "Review clinical documentation for MEAT criteria (Monitor, Evaluate, Assess, Treat)",
            "Consider demographic risk factors when selecting between similar ICD-10 codes"
        ]
        
        if data.patient_age and data.patient_age >= 65:
            action_items.append("Prioritize HCC-eligible codes for Medicare risk adjustment")
            action_items.append("Ensure comprehensive geriatric assessment for Medicare risk adjustment")
        
        # Calculate comprehensive metrics
        total_raf = sum(s.raf_weight for s in suggestions[:3]) if suggestions else 0
        potential_revenue = int(total_raf * 17000)  # Estimated annual revenue per RAF point
        
        # Overall assessment
        if suggestions:
            avg_confidence = sum(s.confidence_score for s in suggestions) / len(suggestions)
            if avg_confidence > 80:
                overall_confidence = "HIGH"
            elif avg_confidence > 60:
                overall_confidence = "MEDIUM" 
            else:
                overall_confidence = "LOW"
            
            priority_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for s in suggestions:
                priority_counts[s.priority_level] += 1
            
            if priority_counts['HIGH'] > 0:
                overall_priority = "HIGH"
            elif priority_counts['MEDIUM'] > 0:
                overall_priority = "MEDIUM"
            else:
                overall_priority = "LOW"
        else:
            overall_confidence = "LOW"
            overall_priority = "LOW"
        
        return HCCAnalysisResponse(
            suggestions=suggestions[:10],
            extracted_conditions=extracted_conditions,
            total_raf_impact=round(total_raf, 3),
            recommendations=recommendations,
            ai_available=ai_available,
            overall_confidence=overall_confidence,
            priority_level=overall_priority,
            potential_revenue_impact=f"${potential_revenue:,}",
            demographic_analysis=demographic_analysis,
            action_items=action_items,
            additional_documentation=additional_documentation or ["Document specific complications and comorbidities", "Include severity indicators and staging", "Note chronic vs acute presentation"],
            # NEW: ICD-10 selection guidance
            hcc_vs_non_hcc_comparison=hcc_vs_non_hcc_comparison,
            top_revenue_opportunities=top_revenue_opportunities,
            documentation_improvement_tips=documentation_improvement_tips
        )
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-legacy", response_model=HCCAnalysisResponse)
async def analyze_physician_input_legacy(input_data: PhysicianInput):
    """Legacy endpoint for backwards compatibility"""
    # Convert legacy format to new format
    analysis_request = AnalysisRequest(
        clinical_notes=input_data.clinical_notes,
        visit_type="Follow-up Visit",  # Default
        primary_diagnosis=input_data.primary_diagnosis,
        provider_name="Dr. Provider",
        patient_history=input_data.patient_history,
        current_icd=input_data.current_icd
    )
    
    return await analyze_notes_intelligently(analysis_request)

@app.get("/demo-scenarios")
async def get_demo_scenarios():
    """Get demo patient scenarios for testing"""
    scenarios = [
        {
            "name": "Diabetic with Kidney Disease",
            "primary_diagnosis": "diabetes",
            "clinical_notes": "Patient has type 2 diabetes with chronic kidney disease stage 3. Blood sugar levels elevated. Creatinine 1.8. Patient on metformin and ACE inhibitor.",
            "current_icd": "E11.9",
            "expected_improvement": "E11.22 (HCC 18, RAF 0.302)"
        },
        {
            "name": "Heart Failure Patient",
            "primary_diagnosis": "shortness of breath",
            "clinical_notes": "Patient presents with dyspnea, pedal edema, and fatigue. Echo shows reduced ejection fraction. History of coronary artery disease.",
            "current_icd": None,
            "expected_improvement": "I50.9 (HCC 85, RAF 0.323)"
        }
    ]
    return scenarios

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)