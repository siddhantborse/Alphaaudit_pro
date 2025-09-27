from database.models import DatabaseManager, HCCMapping

def create_sample_data():
    """Create sample ICD-HCC mappings for demo"""
    
    sample_mappings = [
        # Diabetes conditions
        HCCMapping(
            icd_code="E11.22",
            icd_description="Type 2 diabetes mellitus with diabetic chronic kidney disease",
            hcc_code="HCC 37",
            hcc_description="Diabetes with Chronic Complications",
            raf_weight=0.302,
            category="diabetes"
        ),
        HCCMapping(
            icd_code="E11.51",
            icd_description="Type 2 diabetes mellitus with diabetic peripheral angiopathy without gangrene",
            hcc_code="HCC 37",
            hcc_description="Diabetes with Chronic Complications",
            raf_weight=0.302,
            category="diabetes"
        ),
        HCCMapping(
            icd_code="E11.9",
            icd_description="Type 2 diabetes mellitus without complications",
            hcc_code="HCC 38",
            hcc_description="Diabetes without Complication",
            raf_weight=0.104,
            category="diabetes"
        ),
        
        # Kidney conditions
        HCCMapping(
            icd_code="N18.31",
            icd_description="Chronic kidney disease, stage 3a",
            hcc_code="HCC 327",
            hcc_description="Chronic Kidney Disease Stage 3",
            raf_weight=0.237,
            category="kidney"
        ),
        HCCMapping(
            icd_code="N18.4",
            icd_description="Chronic kidney disease, stage 4 (severe)",
            hcc_code="HCC 326",
            hcc_description="Chronic Kidney Disease Stage 4",
            raf_weight=0.421,
            category="kidney"
        ),
        HCCMapping(
            icd_code="N18.5",
            icd_description="Chronic kidney disease, stage 5",
            hcc_code="HCC 325",
            hcc_description="Chronic Kidney Disease Stage 5",
            raf_weight=0.675,
            category="kidney"
        ),
        
        # Heart conditions
        HCCMapping(
            icd_code="I50.9",
            icd_description="Heart failure, unspecified",
            hcc_code="HCC 223",
            hcc_description="Congestive Heart Failure",
            raf_weight=0.323,
            category="heart"
        ),
        HCCMapping(
            icd_code="I25.10",
            icd_description="Atherosclerotic heart disease of native coronary artery without angina pectoris",
            hcc_code="HCC 224",
            hcc_description="Coronary Artery Disease",
            raf_weight=0.195,
            category="heart"
        ),
        
        # Mental health
        HCCMapping(
            icd_code="F32.1",
            icd_description="Major depressive disorder, single episode, moderate",
            hcc_code="HCC 155",
            hcc_description="Major Depressive and Bipolar Disorders",
            raf_weight=0.309,
            category="mental"
        ),
        HCCMapping(
            icd_code="F32.0",
            icd_description="Major depressive disorder, single episode, mild",
            hcc_code=None,  # No HCC mapping
            hcc_description=None,
            raf_weight=0.0,
            category="mental"
        ),
        
        # COPD/Respiratory
        HCCMapping(
            icd_code="J44.1",
            icd_description="Chronic obstructive pulmonary disease with acute exacerbation",
            hcc_code="HCC 287",
            hcc_description="COPD",
            raf_weight=0.328,
            category="respiratory"
        ),
        
        # Transplant status (High value)
        HCCMapping(
            icd_code="Z94.0",
            icd_description="Kidney transplant status",
            hcc_code="HCC 274",
            hcc_description="Kidney Transplant Status",
            raf_weight=0.525,
            category="transplant"
        ),
    ]
    
    # Keywords for each mapping
    keywords_map = {
        "E11.22": ["diabetes", "type 2", "kidney", "chronic", "renal", "nephropathy"],
        "E11.51": ["diabetes", "type 2", "peripheral", "angiopathy", "circulation"],
        "E11.9": ["diabetes", "type 2", "without complications"],
        "N18.31": ["kidney", "chronic", "stage 3", "ckd", "renal"],
        "N18.4": ["kidney", "chronic", "stage 4", "severe", "ckd", "renal"],
        "N18.5": ["kidney", "chronic", "stage 5", "end stage", "ckd", "renal"],
        "I50.9": ["heart", "failure", "congestive", "chf", "cardiac"],
        "I25.10": ["heart", "coronary", "artery", "atherosclerotic", "cad"],
        "F32.1": ["depression", "major", "moderate", "depressive", "mood"],
        "F32.0": ["depression", "major", "mild", "depressive", "mood"],
        "J44.1": ["copd", "chronic", "obstructive", "pulmonary", "respiratory", "exacerbation"],
        "Z94.0": ["kidney", "transplant", "status", "renal", "transplanted"],
    }
    
    return sample_mappings, keywords_map

def init_database():
    """Initialize database with sample data"""
    print("Initializing HCC Assistant Database...")
    
    db = DatabaseManager()
    sample_mappings, keywords_map = create_sample_data()
    
    # Insert sample data
    for mapping in sample_mappings:
        keywords = keywords_map.get(mapping.icd_code, [])
        db.insert_mapping(mapping, keywords)
    
    print(f"Inserted {len(sample_mappings)} sample ICD-HCC mappings")
    print("Database initialization complete!")

if __name__ == "__main__":
    init_database()
