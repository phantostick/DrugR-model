import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GraniteModel:
    """IBM Granite model handler for medical text analysis"""
    
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME", "ibm-granite/granite-3b-code-instruct-2k")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = int(os.getenv("MAX_LENGTH", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        
        logger.info(f"Initialized Granite model handler: {self.model_name}")
        logger.info(f"Device: {self.device}")
    
    async def load_model(self):
        """Load the IBM Granite model"""
        try:
            logger.info("Loading IBM Granite tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Loading IBM Granite model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device.type == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            self.is_loaded = True
            
            logger.info("IBM Granite model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load IBM Granite model: {str(e)}")
            raise
    
    async def generate_response(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Generate response using IBM Granite model"""
        
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length - max_new_tokens,
                padding=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise
    
    async def extract_drugs(self, prescription_text: str) -> Dict[str, Any]:
        """Extract drug information from prescription text"""
        
        prompt = f"""<|system|>
You are a medical AI assistant specialized in analyzing prescriptions. Extract drug information from the given text.

<|user|>
Analyze this prescription text and extract drug information in JSON format:

Text: "{prescription_text}"

Please provide a JSON response with the following structure:
{{
    "drugs": [
        {{
            "name": "drug_name",
            "dosage": "dosage_amount",
            "frequency": "frequency_info",
            "confidence": 0.95
        }}
    ]
}}

<|assistant|>
"""
        
        response = await self.generate_response(prompt, max_new_tokens=300)
        return self._parse_drug_extraction(response, prescription_text)
    
    def _parse_drug_extraction(self, response: str, original_text: str) -> Dict[str, Any]:
        """Parse drug extraction response"""
        try:
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    if "drugs" in result:
                        return result
                except json.JSONDecodeError:
                    pass
            
            # Fallback: simple pattern matching
            drugs = []
            
            # Common drug name patterns
            drug_patterns = [
                r'\b([A-Z][a-z]+(?:in|ol|ide|ine|ate|pam|zole|cillin))\b',
                r'\b(Aspirin|Ibuprofen|Acetaminophen|Tylenol|Advil)\b',
                r'\b([A-Z][a-z]{3,})\s+\d+\s*mg\b'
            ]
            
            for pattern in drug_patterns:
                matches = re.finditer(pattern, original_text, re.IGNORECASE)
                for match in matches:
                    drug_name = match.group(1)
                    
                    # Extract dosage
                    dosage_pattern = rf'{re.escape(drug_name)}\s+(\d+\s*mg|\d+\s*g)'
                    dosage_match = re.search(dosage_pattern, original_text, re.IGNORECASE)
                    dosage = dosage_match.group(1) if dosage_match else "Not specified"
                    
                    # Extract frequency
                    freq_patterns = [
                        r'(once daily|twice daily|three times daily|every \d+ hours)',
                        r'(daily|bid|tid|qid|q\d+h)'
                    ]
                    frequency = "Not specified"
                    for freq_pattern in freq_patterns:
                        freq_match = re.search(freq_pattern, original_text, re.IGNORECASE)
                        if freq_match:
                            frequency = freq_match.group(1)
                            break
                    
                    drugs.append({
                        "name": drug_name,
                        "dosage": dosage,
                        "frequency": frequency,
                        "confidence": 0.8
                    })
            
            return {"drugs": drugs}
            
        except Exception as e:
            logger.error(f"Failed to parse drug extraction: {str(e)}")
            return {"drugs": []}