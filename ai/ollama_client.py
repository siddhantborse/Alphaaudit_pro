import requests
import json
from typing import List, Dict, Optional

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "llama3.2:3b"  # Lightweight model for fast inference
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def extract_medical_conditions(self, text: str) -> Dict:
        """Extract medical conditions and keywords from physician notes"""
        
        prompt = f"""
You are a medical coding assistant. Analyze the following physician notes and extract:
1. Primary diagnosis/condition
2. Secondary conditions
3. Key medical terms
4. Severity indicators
5. Chronic vs acute status

Physician Notes: "{text}"

Respond in JSON format:
{{
    "primary_condition": "main diagnosis",
    "secondary_conditions": ["condition1", "condition2"],
    "medical_keywords": ["keyword1", "keyword2"],
    "severity": "mild/moderate/severe",
    "chronicity": "acute/chronic/unknown",
    "extracted_terms": ["specific medical terms found"]
}}
"""
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                try:
                    return json.loads(result['response'])
                except:
                    # Fallback parsing
                    return self._fallback_extraction(text)
            else:
                return self._fallback_extraction(text)
                
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._fallback_extraction(text)
    
    def _fallback_extraction(self, text: str) -> Dict:
        """Fallback extraction using keyword matching"""
        text_lower = text.lower()
        
        # Common medical condition keywords
        diabetes_terms = ['diabetes', 'diabetic', 'dm', 'type 2', 't2dm']
        kidney_terms = ['kidney', 'renal', 'ckd', 'nephropathy']
        heart_terms = ['heart', 'cardiac', 'chf', 'coronary', 'cad']
        depression_terms = ['depression', 'depressive', 'mood', 'psychiatric']
        
        conditions = []
        keywords = []
        
        if any(term in text_lower for term in diabetes_terms):
            conditions.append('diabetes')
            keywords.extend(['diabetes', 'type 2'])
            
        if any(term in text_lower for term in kidney_terms):
            conditions.append('kidney disease')
            keywords.extend(['kidney', 'chronic', 'renal'])
            
        if any(term in text_lower for term in heart_terms):
            conditions.append('heart disease')
            keywords.extend(['heart', 'cardiac'])
            
        if any(term in text_lower for term in depression_terms):
            conditions.append('depression')
            keywords.extend(['depression', 'depressive'])
        
        # Determine severity
        severity = "unknown"
        if any(word in text_lower for word in ['severe', 'advanced', 'stage 4', 'stage 5']):
            severity = "severe"
        elif any(word in text_lower for word in ['moderate', 'stage 3']):
            severity = "moderate"
        elif any(word in text_lower for word in ['mild', 'stage 1', 'stage 2']):
            severity = "mild"
        
        # Determine chronicity
        chronicity = "unknown"
        if any(word in text_lower for word in ['chronic', 'long-term', 'ongoing']):
            chronicity = "chronic"
        elif any(word in text_lower for word in ['acute', 'sudden', 'recent']):
            chronicity = "acute"
        
        return {
            "primary_condition": conditions[0] if conditions else "unknown",
            "secondary_conditions": conditions[1:],
            "medical_keywords": list(set(keywords)),
            "severity": severity,
            "chronicity": chronicity,
            "extracted_terms": conditions
        }
    
    def suggest_icd_improvement(self, current_icd: str, available_options: List[Dict]) -> str:
        """Suggest better ICD code based on available options"""
        
        if not available_options:
            return "No better options available."
        
        # Find highest RAF weight option
        best_option = max(available_options, key=lambda x: x.get('raf_weight', 0))
        
        return f"Consider {best_option['icd_code']} ({best_option['hcc_description']}) for RAF weight {best_option['raf_weight']}"
