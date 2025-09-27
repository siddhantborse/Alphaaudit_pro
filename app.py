from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json

from database.models import DatabaseManager, HCCMapping
from ai.ollama_client import OllamaClient

app = FastAPI(title="HCC Coding Assistant API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
ai_client = OllamaClient()

# Pydantic models for API
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

class HCCAnalysisResponse(BaseModel):
    suggestions: List[ICDSuggestion]
    extracted_conditions: Dict
    total_raf_impact: float
    recommendations: List[str]
    ai_available: bool

@app.get("/")
async def root():
    return {
        "message": "HCC Coding Assistant API",
        "version": "1.0.0",
        "ai_status": ai_client.is_available()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_available": ai_client.is_available(),
        "database_ready": True
    }

@app.post("/analyze", response_model=HCCAnalysisResponse)
async def analyze_physician_input(input_data: PhysicianInput):
    """Main endpoint: Analyze physician input and suggest optimal ICD codes"""
    
    try:
        # Combine all input text for analysis
        full_text = f"{input_data.primary_diagnosis} {input_data.clinical_notes}"
        if input_data.patient_history:
            full_text += f" {input_data.patient_history}"
        
        # Extract conditions using AI (if available) or fallback
        extracted_conditions = ai_client.extract_medical_conditions(full_text)
        
        # Search for relevant ICD-HCC mappings
        search_keywords = extracted_conditions.get('medical_keywords', [])
        search_keywords.extend(extracted_conditions.get('extracted_terms', []))
        search_keywords.append(input_data.primary_diagnosis.lower())
        
        # Remove duplicates and search
        unique_keywords = list(set(search_keywords))
        mappings = db.search_by_keywords(unique_keywords)
        
        # Convert to suggestions with confidence scoring
        suggestions = []
        for mapping in mappings:
            confidence = calculate_confidence_score(mapping, extracted_conditions)
            reasoning = generate_reasoning(mapping, extracted_conditions)
            
            suggestion = ICDSuggestion(
                icd_code=mapping.icd_code,
                description=mapping.icd_description,
                hcc_code=mapping.hcc_code,
                hcc_description=mapping.hcc_description,
                raf_weight=mapping.raf_weight,
                confidence_score=confidence,
                reasoning=reasoning
            )
            suggestions.append(suggestion)
        
        # Sort by RAF weight and confidence
        suggestions.sort(key=lambda x: (x.raf_weight, x.confidence_score), reverse=True)
        
        # Generate recommendations
        recommendations = generate_recommendations(input_data, suggestions, extracted_conditions)
        
        # Calculate total RAF impact
        total_raf = sum(s.raf_weight for s in suggestions[:3])  # Top 3 suggestions
        
        return HCCAnalysisResponse(
            suggestions=suggestions[:10],  # Limit to top 10
            extracted_conditions=extracted_conditions,
            total_raf_impact=total_raf,
            recommendations=recommendations,
            ai_available=ai_client.is_available()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/icd/{icd_code}")
async def get_icd_info(icd_code: str):
    """Get detailed information about a specific ICD code"""
    mapping = db.get_hcc_info(icd_code)
    if not mapping:
        raise HTTPException(status_code=404, detail="ICD code not found")
    
    return {
        "icd_code": mapping.icd_code,
        "description": mapping.icd_description,
        "hcc_code": mapping.hcc_code,
        "hcc_description": mapping.hcc_description,
        "raf_weight": mapping.raf_weight,
        "category": mapping.category
    }

@app.get("/demo-scenarios")
async def get_demo_scenarios():
    """Get demo patient scenarios for testing"""
    scenarios = [
        {
            "name": "Diabetic with Kidney Disease",
            "primary_diagnosis": "diabetes",
            "clinical_notes": "Patient has type 2 diabetes with chronic kidney disease stage 3. Blood sugar levels elevated. Creatinine 1.8. Patient on metformin and ACE inhibitor.",
            "current_icd": "E11.9",
            "expected_improvement": "E11.22 (HCC 37, RAF 0.302)"
        },
        {
            "name": "Heart Failure Patient",
            "primary_diagnosis": "shortness of breath",
            "clinical_notes": "Patient presents with dyspnea, pedal edema, and fatigue. Echo shows reduced ejection fraction. History of coronary artery disease.",
            "current_icd": None,
            "expected_improvement": "I50.9 (HCC 223, RAF 0.323)"
        },
        {
            "name": "Depression - Severity Matters",
            "primary_diagnosis": "depression",
            "clinical_notes": "Patient reports persistent sad mood, loss of interest, sleep disturbance, and difficulty concentrating for past 8 weeks. Moderate severity affecting daily functioning.",
            "current_icd": "F32.0",
            "expected_improvement": "F32.1 (HCC 155, RAF 0.309)"
        },
        {
            "name": "Kidney Transplant Status",
            "primary_diagnosis": "routine follow-up",
            "clinical_notes": "Patient with history of kidney transplant 3 years ago. Currently stable on immunosuppressive therapy. Creatinine stable at 1.2.",
            "current_icd": None,
            "expected_improvement": "Z94.0 (HCC 274, RAF 0.525)"
        }
    ]
    return scenarios

def calculate_confidence_score(mapping: HCCMapping, extracted_conditions: Dict) -> float:
    """Calculate confidence score for ICD suggestion"""
    score = 0.5  # Base score
    
    # Boost score based on keyword matches
    keywords = extracted_conditions.get('medical_keywords', [])
    for keyword in keywords:
        if keyword.lower() in mapping.icd_description.lower():
            score += 0.1
    
    # Boost for chronicity match
    if extracted_conditions.get('chronicity') == 'chronic' and 'chronic' in mapping.icd_description.lower():
        score += 0.2
    
    # Boost for severity match
    severity = extracted_conditions.get('severity', '')
    if severity in ['severe', 'moderate'] and any(word in mapping.icd_description.lower() 
                                                  for word in ['severe', 'stage 4', 'stage 5']):
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0

def generate_reasoning(mapping: HCCMapping, extracted_conditions: Dict) -> str:
    """Generate human-readable reasoning for ICD suggestion"""
    reasoning_parts = []
    
    if mapping.hcc_code:
        reasoning_parts.append(f"Maps to {mapping.hcc_code} with RAF weight {mapping.raf_weight}")
    else:
        reasoning_parts.append("Does not map to HCC (no RAF value)")
    
    # Add specificity note
    if 'without' in mapping.icd_description.lower():
        reasoning_parts.append("Consider if complications are present for higher RAF value")
    
    return ". ".join(reasoning_parts)

def generate_recommendations(input_data: PhysicianInput, suggestions: List[ICDSuggestion], 
                           extracted_conditions: Dict) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if not suggestions:
        recommendations.append("No HCC-eligible conditions found. Consider reviewing for chronic conditions.")
        return recommendations
    
    # Top suggestion
    if suggestions:
        top = suggestions[0]
        if top.raf_weight > 0:
            recommendations.append(
                f"RECOMMENDED: Use {top.icd_code} for {top.raf_weight} RAF weight ({top.hcc_description})"
            )
    
    # Chronicity recommendation
    if extracted_conditions.get('chronicity') == 'chronic':
        recommendations.append("✓ Chronic condition identified - ensure annual HCC recapture")
    
    # MEAT documentation
    recommendations.append("Ensure MEAT criteria documented: Monitor, Evaluate, Assess, Treat")
    
    # Missing current ICD comparison
    if input_data.current_icd:
        current_mapping = db.get_hcc_info(input_data.current_icd)
        if current_mapping and suggestions:
            top_suggestion = suggestions[0]
            if top_suggestion.raf_weight > (current_mapping.raf_weight or 0):
                improvement = top_suggestion.raf_weight - (current_mapping.raf_weight or 0)
                annual_value = improvement * 17000  # Rough annual dollar impact
                recommendations.append(
                    f"UPGRADE OPPORTUNITY: Switch from {input_data.current_icd} to {top_suggestion.icd_code} "
                    f"for +{improvement:.3f} RAF weight (~${annual_value:,.0f} annual impact)"
                )
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
