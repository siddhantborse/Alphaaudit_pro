import sqlite3
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ICDCode:
    code: str
    description: str
    hcc_code: Optional[str] = None
    hcc_description: Optional[str] = None
    raf_weight: Optional[float] = None
    is_chronic: bool = False

@dataclass
class HCCMapping:
    icd_code: str
    icd_description: str
    hcc_code: str
    hcc_description: str
    raf_weight: float
    category: str  # e.g., 'diabetes', 'kidney', 'heart'

class DatabaseManager:
    def __init__(self, db_path: str = "hcc_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create ICD-HCC mapping table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS icd_hcc_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icd_code TEXT NOT NULL,
            icd_description TEXT NOT NULL,
            hcc_code TEXT,
            hcc_description TEXT,
            raf_weight REAL DEFAULT 0.0,
            category TEXT,
            is_chronic BOOLEAN DEFAULT 0,
            keywords TEXT  -- Space-separated keywords for search
        )
        ''')
        
        # Create index for faster search
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords ON icd_hcc_mappings(keywords)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON icd_hcc_mappings(category)')
        
        conn.commit()
        conn.close()
    
    def search_by_keywords(self, keywords: List[str]) -> List[HCCMapping]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build search query
        search_terms = [f"keywords LIKE '%{kw.lower()}%'" for kw in keywords]
        query = f'''
        SELECT icd_code, icd_description, hcc_code, hcc_description, raf_weight, category
        FROM icd_hcc_mappings 
        WHERE ({' OR '.join(search_terms)}) AND hcc_code IS NOT NULL
        ORDER BY raf_weight DESC
        LIMIT 10
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return [HCCMapping(*row) for row in results]
    
    def get_hcc_info(self, icd_code: str) -> Optional[HCCMapping]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT icd_code, icd_description, hcc_code, hcc_description, raf_weight, category
        FROM icd_hcc_mappings 
        WHERE icd_code = ?
        ''', (icd_code,))
        
        result = cursor.fetchone()
        conn.close()
        
        return HCCMapping(*result) if result else None
    
    def insert_mapping(self, mapping: HCCMapping, keywords: List[str]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO icd_hcc_mappings 
        (icd_code, icd_description, hcc_code, hcc_description, raf_weight, category, keywords, is_chronic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mapping.icd_code, mapping.icd_description, mapping.hcc_code, 
            mapping.hcc_description, mapping.raf_weight, mapping.category,
            ' '.join(keywords).lower(), 1
        ))
        
        conn.commit()
        conn.close()
