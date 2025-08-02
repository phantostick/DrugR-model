from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import time
from datetime import datetime
import logging

from models.granite_model import GraniteModel
from models.drug_analyzer import DrugAnalyzer
from data.drug_database import DrugDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Medical Prescription Verifier",
    description="Advanced prescription analysis using IBM Granite models",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
granite_model = None
drug_analyzer = None
drug_db = None

class PrescriptionRequest(BaseModel):
    text: str
    age: int
    weight: Optional[float] = None
    medical_conditions: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    models_loaded: Dict[str, bool]
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global granite_model, drug_analyzer, drug_db
    
    logger.info("Initializing AI models...")
    
    try:
        # Initialize IBM Granite model
        granite_model = GraniteModel()
        await granite_model.load_model()
        
        # Initialize drug database
        drug_db = DrugDatabase()
        drug_db.initialize()
        
        # Initialize drug analyzer
        drug_analyzer = DrugAnalyzer(granite_model, drug_db)
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        models_loaded={
            "granite_model": granite_model is not None and granite_model.is_loaded,
            "drug_database": drug_db is not None,
            "drug_analyzer": drug_analyzer is not None
        },
        timestamp=datetime.now().isoformat()
    )

@app.post("/analyze")
async def analyze_prescription(request: PrescriptionRequest):
    """Analyze prescription using IBM Granite model"""
    
    if not granite_model or not granite_model.is_loaded:
        raise HTTPException(status_code=503, detail="Granite model not loaded")
    
    if not drug_analyzer:
        raise HTTPException(status_code=503, detail="Drug analyzer not initialized")
    
    start_time = time.time()
    
    try:
        # Analyze prescription
        analysis_result = await drug_analyzer.analyze_prescription(
            text=request.text,
            patient_age=request.age,
            patient_weight=request.weight,
            medical_conditions=request.medical_conditions or []
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            **analysis_result,
            "processing_time_ms": processing_time,
            "timestamp": datetime.now().isoformat(),
            "model_info": {
                "model_name": granite_model.model_name,
                "model_version": "granite-2b-instruct"
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )