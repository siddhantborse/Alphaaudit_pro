# HCC Code Assistant - Project Structure

```
hcc_assistant/
├── app.py                 # Main FastAPI backend
├── database/
│   ├── init_db.py        # Database initialization
│   ├── models.py         # Database models
│   └── sample_data.py    # Sample ICD-HCC mappings
├── ai/
│   ├── ollama_client.py  # OLLAMA integration
│   └── prompts.py        # AI prompt templates
├── frontend/
│   └── streamlit_app.py  # GUI interface
├── static/
│   └── demo_data.json    # Sample patient scenarios
└── requirements.txt
```

## Quick Start Commands:
1. `pip install -r requirements.txt`
2. `python database/init_db.py`
3. `uvicorn app:app --reload` (Backend)
4. `streamlit run frontend/streamlit_app.py` (Frontend)
