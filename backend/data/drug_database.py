from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)

class DrugDatabase:
    """Drug interactions and information database"""
    
    def __init__(self):
        self.interactions = {}
        self.drug_classes = {}
        self.contraindications = {}
    
    def initialize(self):
        """Initialize database with seed data"""
        self._load_interactions()
        self._load_drug_classes()
        self._load_contraindications()
        logger.info("Drug database initialized")
    
    def _load_interactions(self):
        """Load known drug interactions"""
        self.interactions = {
            # ACE Inhibitors + Diuretics
            ("lisinopril", "hydrochlorothiazide"): {
                "severity": "MEDIUM",
                "warning": "May cause excessive reduction in blood pressure",
                "recommendation": "Monitor blood pressure closely"
            },
            
            # Warfarin interactions
            ("warfarin", "aspirin"): {
                "severity": "HIGH",
                "warning": "Increased risk of bleeding",
                "recommendation": "Consider alternative or reduce warfarin dose"
            },
            
            ("warfarin", "ibuprofen"): {
                "severity": "HIGH",
                "warning": "NSAIDs increase bleeding risk with warfarin",
                "recommendation": "Avoid concurrent use or monitor INR closely"
            },
            
            # NSAIDs combinations
            ("ibuprofen", "aspirin"): {
                "severity": "MEDIUM",
                "warning": "Increased risk of GI bleeding and reduced cardioprotective effect",
                "recommendation": "Consider timing separation or alternative"
            },
            
            ("ibuprofen", "acetaminophen"): {
                "severity": "LOW",
                "warning": "Generally safe combination",
                "recommendation": "Monitor for hepatotoxicity with high doses"
            },
            
            # Diabetes medications
            ("metformin", "gliclazide"): {
                "severity": "LOW",
                "warning": "Additive hypoglycemic effect",
                "recommendation": "Monitor blood glucose levels"
            },
            
            # Hypertension combinations
            ("amlodipine", "lisinopril"): {
                "severity": "LOW",
                "warning": "Complementary antihypertensive effects",
                "recommendation": "Good combination, monitor blood pressure"
            },
            
            # Statins + Other drugs
            ("atorvastatin", "amlodipine"): {
                "severity": "MEDIUM",
                "warning": "Amlodipine may increase atorvastatin levels",
                "recommendation": "Consider lower atorvastatin dose"
            }
        }
    
    def _load_drug_classes(self):
        """Load drug classifications"""
        self.drug_classes = {
            "lisinopril": "ACE Inhibitor",
            "amlodipine": "Calcium Channel Blocker",
            "hydrochlorothiazide": "Thiazide Diuretic",
            "metformin": "Biguanide",
            "gliclazide": "Sulfonylurea",
            "warfarin": "Anticoagulant",
            "aspirin": "Antiplatelet/NSAID",
            "ibuprofen": "NSAID",
            "acetaminophen": "Analgesic/Antipyretic",
            "atorvastatin": "Statin",
            "omeprazole": "Proton Pump Inhibitor",
            "levothyroxine": "Thyroid Hormone",
            "prednisone": "Corticosteroid"
        }
    
    def _load_contraindications(self):
        """Load contraindications"""
        self.contraindications = {
            "aspirin": ["asthma", "bleeding disorders", "peptic ulcer"],
            "ibuprofen": ["kidney disease", "heart failure", "asthma"],
            "metformin": ["kidney disease", "liver disease"],
            "warfarin": ["bleeding disorders", "liver disease"],
            "lisinopril": ["angioedema", "pregnancy", "hyperkalemia"]
        }
    
    def check_interactions(self, drug_names: List[str]) -> List[Dict]:
        """Check for known interactions between drugs"""
        interactions = []
        
        for i, drug1 in enumerate(drug_names):
            for drug2 in drug_names[i+1:]:
                interaction = self._get_interaction(drug1.lower(), drug2.lower())
                if interaction:
                    interactions.append({
                        "drug1": drug1.title(),
                        "drug2": drug2.title(),
                        **interaction
                    })
        
        return interactions
    
    def _get_interaction(self, drug1: str, drug2: str) -> Dict:
        """Get interaction between two drugs"""
        # Check both combinations
        interaction = (self.interactions.get((drug1, drug2)) or 
                      self.interactions.get((drug2, drug1)))
        return interaction
    
    def get_drug_class(self, drug_name: str) -> str:
        """Get drug classification"""
        return self.drug_classes.get(drug_name.lower(), "Unknown")
    
    def get_contraindications(self, drug_name: str) -> List[str]:
        """Get contraindications for a drug"""
        return self.contraindications.get(drug_name.lower(), [])