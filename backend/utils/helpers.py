"""
Utility functions for the medical prescription analyzer
"""
import re
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def clean_drug_name(drug_name: str) -> str:
    """Clean and standardize drug names"""
    if not drug_name:
        return ""
    
    # Remove extra whitespace and convert to title case
    cleaned = re.sub(r'\s+', ' ', drug_name.strip()).title()
    
    # Remove common suffixes that might interfere with matching
    suffixes_to_remove = ['Hcl', 'Hct', 'Er', 'Xl', 'Sr', 'La']
    for suffix in suffixes_to_remove:
        pattern = rf'\s+{suffix}'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned

def extract_dosage_from_text(text: str, drug_name: str) -> Optional[str]:
    """Extract dosage information for a specific drug from text"""
    if not text or not drug_name:
        return None
    
    # Pattern to match dosage near drug name
    patterns = [
        rf'{re.escape(drug_name)}\s+(\d+(?:\.\d+)?\s*(?:mg|g|mcg|units?))',
        rf'(\d+(?:\.\d+)?\s*(?:mg|g|mcg|units?))\s+{re.escape(drug_name)}',
        rf'{re.escape(drug_name)}.*?(\d+(?:\.\d+)?\s*(?:mg|g|mcg|units?))'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_frequency_from_text(text: str) -> Optional[str]:
    """Extract frequency/timing information from prescription text"""
    if not text:
        return None
    
    frequency_patterns = [
        r'\b(once\s+daily|twice\s+daily|three\s+times\s+daily|four\s+times\s+daily)\b',
        r'\b(daily|bid|tid|qid|q\d+h|every\s+\d+\s+hours?)\b',
        r'\b(morning|evening|bedtime|with\s+meals?|after\s+meals?|before\s+meals?)\b',
        r'\b(as\s+needed|prn|when\s+required)\b'
    ]
    
    frequencies = []
    for pattern in frequency_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        frequencies.extend(matches)
    
    return ', '.join(set(frequencies)) if frequencies else None

def calculate_age_category(age: int) -> str:
    """Calculate age category for dosing purposes"""
    if age < 0:
        return "Invalid"
    elif age < 1:
        return "Neonate"
    elif age < 2:
        return "Infant"
    elif age < 12:
        return "Child"
    elif age < 18:
        return "Adolescent"
    elif age < 65:
        return "Adult"
    else:
        return "Elderly"

def format_confidence_level(confidence: float) -> str:
    """Format confidence score as descriptive text"""
    if confidence >= 0.9:
        return "Very High"
    elif confidence >= 0.8:
        return "High"
    elif confidence >= 0.7:
        return "Medium"
    elif confidence >= 0.6:
        return "Moderate"
    else:
        return "Low"

def validate_prescription_text(text: str) -> Dict[str, Any]:
    """Validate prescription text and provide feedback"""
    if not text or not text.strip():
        return {
            "is_valid": False,
            "errors": ["Prescription text is empty"],
            "suggestions": ["Please enter a prescription to analyze"]
        }
    
    errors = []
    suggestions = []
    warnings = []
    
    # Check minimum length
    if len(text.strip()) < 10:
        warnings.append("Prescription text seems very short")
        suggestions.append("Consider providing more detailed prescription information")
    
    # Check for common drug name patterns
    drug_pattern = r'\b[A-Z][a-z]+(?:in|ol|ide|ine|ate|pam|zole|cillin|mycin)\b'
    potential_drugs = re.findall(drug_pattern, text)
    
    if not potential_drugs:
        warnings.append("No obvious drug names detected")
        suggestions.append("Ensure drug names are properly spelled and formatted")
    
    # Check for dosage information
    dosage_pattern = r'\d+\s*(?:mg|g|mcg|units?|ml|tablets?|capsules?)'
    if not re.search(dosage_pattern, text, re.IGNORECASE):
        warnings.append("No dosage information detected")
        suggestions.append("Include dosage amounts (e.g., 10mg, 500mg)")
    
    # Check for frequency information
    frequency_patterns = [
        r'\b(?:once|twice|three times|daily|bid|tid|qid)\b',
        r'\bevery\s+\d+\s+hours?\b',
        r'\b(?:morning|evening|bedtime)\b'
    ]
    
    has_frequency = any(re.search(pattern, text, re.IGNORECASE) for pattern in frequency_patterns)
    if not has_frequency:
        warnings.append("No frequency information detected")
        suggestions.append("Include dosing frequency (e.g., once daily, twice daily)")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "detected_drugs": len(potential_drugs),
        "estimated_complexity": "High" if len(potential_drugs) > 3 else "Medium" if len(potential_drugs) > 1 else "Low"
    }

def safe_json_parse(text: str) -> Optional[Dict]:
    """Safely parse JSON from text, handling common formatting issues"""
    if not text:
        return None
    
    try:
        # First, try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Try to find JSON within the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    
    try:
        # Try to fix common JSON issues
        cleaned_text = text.strip()
        # Fix single quotes to double quotes
        cleaned_text = re.sub(r"'([^']*)':", r'"\1":', cleaned_text)
        cleaned_text = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned_text)
        # Remove trailing commas
        cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
        
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON: {text[:100]}...")
        return None

def calculate_drug_similarity(drug1: str, drug2: str) -> float:
    """Calculate similarity between drug names (simple Levenshtein-based)"""
    if not drug1 or not drug2:
        return 0.0
    
    drug1, drug2 = drug1.lower(), drug2.lower()
    
    if drug1 == drug2:
        return 1.0
    
    # Simple character-based similarity
    len1, len2 = len(drug1), len(drug2)
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 1.0
    
    # Count matching characters at same positions
    matches = sum(c1 == c2 for c1, c2 in zip(drug1, drug2))
    
    return matches / max_len

def generate_analysis_summary(analysis_result: Dict[str, Any]) -> str:
    """Generate a human-readable summary of the analysis"""
    drugs_count = len(analysis_result.get('extracted_drugs', []))
    interactions_count = len(analysis_result.get('interactions', []))
    warnings_count = len(analysis_result.get('warnings', []))
    
    summary_parts = []
    
    # Drugs summary
    if drugs_count == 0:
        summary_parts.append("No drugs were detected in the prescription.")
    elif drugs_count == 1:
        summary_parts.append("1 medication was identified.")
    else:
        summary_parts.append(f"{drugs_count} medications were identified.")
    
    # Interactions summary
    if interactions_count > 0:
        high_risk = sum(1 for i in analysis_result.get('interactions', []) 
                       if i.get('severity') == 'HIGH')
        if high_risk > 0:
            summary_parts.append(f"{high_risk} high-risk drug interactions detected.")
        else:
            summary_parts.append(f"{interactions_count} potential drug interactions found.")
    
    # Warnings summary
    if warnings_count > 0:
        summary_parts.append(f"{warnings_count} important warnings generated.")
    
    # Overall assessment
    if warnings_count > 0 or interactions_count > 0:
        summary_parts.append("Review recommended before dispensing.")
    else:
        summary_parts.append("No major concerns identified.")
    
    return " ".join(summary_parts)