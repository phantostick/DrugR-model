import asyncio
import json
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DrugAnalyzer:
    """Advanced drug analysis using IBM Granite model"""
    
    def __init__(self, granite_model, drug_database):
        self.granite_model = granite_model
        self.drug_db = drug_database
    
    async def analyze_prescription(
        self,
        text: str,
        patient_age: int,
        patient_weight: Optional[float] = None,
        medical_conditions: List[str] = None
    ) -> Dict[str, Any]:
        """Complete prescription analysis"""
        
        medical_conditions = medical_conditions or []
        
        # Extract drugs using Granite model
        drug_extraction = await self.granite_model.extract_drugs(text)
        extracted_drugs = self._format_extracted_drugs(drug_extraction.get("drugs", []))
        
        # Analyze interactions
        interactions = await self._analyze_interactions(extracted_drugs)
        
        # Generate dosage recommendations
        dosage_recommendations = await self._generate_dosage_recommendations(
            extracted_drugs, patient_age, patient_weight
        )
        
        # Find alternatives
        alternatives = await self._find_alternatives(extracted_drugs, medical_conditions)
        
        # Generate AI insights
        ai_insights = self._generate_ai_insights(extracted_drugs, text)
        
        # Check for warnings
        warnings = self._generate_warnings(extracted_drugs, interactions, patient_age)
        
        return {
            "extracted_drugs": extracted_drugs,
            "interactions": interactions,
            "dosage_recommendations": dosage_recommendations,
            "alternatives": alternatives,
            "ai_insights": ai_insights,
            "warnings": warnings
        }
    
    def _format_extracted_drugs(self, drugs: List[Dict]) -> List[Dict]:
        """Format extracted drugs for frontend display"""
        formatted_drugs = []
        
        for drug in drugs:
            formatted_drug = {
                "word": drug.get("name", "Unknown"),
                "confidence": drug.get("confidence", 0.8),
                "sources": ["granite"],
                "dosage": drug.get("dosage", "Not specified"),
                "frequency": drug.get("frequency", "Not specified"),
                "sentiment": "Neutral"
            }
            formatted_drugs.append(formatted_drug)
        
        return formatted_drugs
    
    async def _analyze_interactions(self, drugs: List[Dict]) -> List[Dict]:
        """Analyze drug interactions using Granite model"""
        if len(drugs) < 2:
            return []
        
        interactions = []
        drug_names = [drug["word"] for drug in drugs]
        
        # Check database interactions first
        db_interactions = self.drug_db.check_interactions(drug_names)
        interactions.extend(db_interactions)
        
        # Use Granite model for additional analysis
        for i, drug1 in enumerate(drugs):
            for drug2 in drugs[i+1:]:
                try:
                    interaction = await self._check_drug_pair_interaction(
                        drug1["word"], drug2["word"]
                    )
                    if interaction:
                        interactions.append(interaction)
                except Exception as e:
                    logger.error(f"Error checking interaction {drug1['word']} - {drug2['word']}: {e}")
        
        return interactions
    
    async def _check_drug_pair_interaction(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check interaction between two drugs using Granite model"""
        
        prompt = f"""<|system|>
You are a clinical pharmacist AI. Analyze potential drug interactions.

<|user|>
Analyze the interaction between {drug1} and {drug2}.

Provide a JSON response:
{{
    "has_interaction": true/false,
    "severity": "HIGH/MEDIUM/LOW",
    "warning": "description of interaction",
    "recommendation": "clinical recommendation"
}}

<|assistant|>
"""
        
        try:
            response = await self.granite_model.generate_response(prompt, max_new_tokens=200)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    if result.get("has_interaction", False):
                        return {
                            "drug1": drug1,
                            "drug2": drug2,
                            "severity": result.get("severity", "MEDIUM"),
                            "warning": result.get("warning", "Potential interaction detected"),
                            "recommendation": result.get("recommendation", "Consult healthcare provider")
                        }
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to analyze interaction {drug1}-{drug2}: {e}")
        
        return None
    
    async def _generate_dosage_recommendations(
        self, drugs: List[Dict], age: int, weight: Optional[float]
    ) -> List[Dict]:
        """Generate age-appropriate dosage recommendations"""
        
        recommendations = []
        age_category = self._get_age_category(age)
        
        for drug in drugs:
            try:
                recommendation = await self._get_dosage_recommendation(
                    drug["word"], age, age_category, weight
                )
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Error generating dosage for {drug['word']}: {e}")
        
        return recommendations
    
    def _get_age_category(self, age: int) -> str:
        """Categorize patient by age"""
        if age < 2:
            return "Infant"
        elif age < 12:
            return "Child"
        elif age < 18:
            return "Adolescent"
        elif age < 65:
            return "Adult"
        else:
            return "Elderly"
    
    async def _get_dosage_recommendation(
        self, drug_name: str, age: int, age_category: str, weight: Optional[float]
    ) -> Optional[Dict]:
        """Get dosage recommendation for specific drug and patient"""
        
        weight_info = f" (weight: {weight}kg)" if weight else ""
        
        prompt = f"""<|system|>
You are a clinical pharmacist providing dosage recommendations.

<|user|>
Provide dosage recommendation for {drug_name} for a {age}-year-old {age_category.lower()} patient{weight_info}.

Respond in JSON format:
{{
    "drug": "{drug_name}",
    "age_category": "{age_category}",
    "recommendation": "dosage recommendation",
    "warnings": ["warning1", "warning2"],
    "monitoring": ["monitoring requirement1"]
}}

<|assistant|>
"""
        
        try:
            response = await self.granite_model.generate_response(prompt, max_new_tokens=250)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Fallback recommendation
            return {
                "drug": drug_name,
                "age_category": age_category,
                "recommendation": f"Standard adult dosing may need adjustment for {age_category.lower()} patients",
                "warnings": ["Consult healthcare provider for appropriate dosing"],
                "monitoring": ["Regular monitoring recommended"]
            }
            
        except Exception as e:
            logger.error(f"Failed to get dosage recommendation for {drug_name}: {e}")
            return None
    
    async def _find_alternatives(
        self, drugs: List[Dict], medical_conditions: List[str]
    ) -> Dict[str, Dict]:
        """Find alternative medications"""
        
        alternatives = {}
        conditions_str = ", ".join(medical_conditions) if medical_conditions else "none"
        
        for drug in drugs[:3]:  # Limit to first 3 drugs for performance
            try:
                alt_info = await self._get_drug_alternatives(drug["word"], conditions_str)
                if alt_info:
                    alternatives[drug["word"]] = alt_info
            except Exception as e:
                logger.error(f"Error finding alternatives for {drug['word']}: {e}")
        
        return alternatives
    
    async def _get_drug_alternatives(self, drug_name: str, conditions: str) -> Optional[Dict]:
        """Get alternatives for a specific drug"""
        
        prompt = f"""<|system|>
You are a clinical pharmacist suggesting drug alternatives.

<|user|>
Suggest alternatives for {drug_name} considering patient conditions: {conditions}

Provide JSON response:
{{
    "original_drug": "{drug_name}",
    "drug_class": "therapeutic class",
    "reason_for_alternatives": "reason",
    "alternatives": [
        {{"name": "alt1", "dosage": "dose", "notes": "notes"}},
        {{"name": "alt2", "dosage": "dose", "notes": "notes"}}
    ],
    "considerations": ["consideration1", "consideration2"]
}}

<|assistant|>
"""
        
        try:
            response = await self.granite_model.generate_response(prompt, max_new_tokens=300)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to get alternatives for {drug_name}: {e}")
        
        return None
    
    def _generate_ai_insights(self, drugs: List[Dict], original_text: str) -> Dict[str, Any]:
        """Generate AI insights about the analysis"""
        
        return {
            "extraction_method": "IBM Granite 2B Instruct Model",
            "models_used": ["granite"],
            "prescription_complexity": "Medium" if len(drugs) > 2 else "Simple",
            "total_drugs_found": len(drugs),
            "confidence_scores": {
                drug["word"]: drug["confidence"] for drug in drugs
            }
        }
    
    def _generate_warnings(
        self, drugs: List[Dict], interactions: List[Dict], age: int
    ) -> List[str]:
        """Generate important warnings"""
        
        warnings = []
        
        # High-risk interactions
        high_risk_interactions = [i for i in interactions if i.get("severity") == "HIGH"]
        if high_risk_interactions:
            warnings.append(f"⚠️ {len(high_risk_interactions)} high-risk drug interactions detected!")
        
        # Age-related warnings
        if age < 18:
            warnings.append("⚠️ Pediatric patient - dosages may need adjustment")
        elif age > 65:
            warnings.append("⚠️ Elderly patient - increased risk of adverse effects")
        
        # Too many medications
        if len(drugs) > 5:
            warnings.append("⚠️ Polypharmacy detected - review for potential drug interactions")
        
        return warnings