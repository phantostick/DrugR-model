"""
Seed data for the medical prescription system
This module contains comprehensive drug information for testing
"""

SAMPLE_PRESCRIPTIONS = [
    {
        "id": 1,
        "title": "Hypertension Management",
        "prescription": "Lisinopril 10mg once daily in the morning, Amlodipine 5mg once daily, Hydrochlorothiazide 25mg once daily",
        "patient_age": 55,
        "conditions": ["hypertension"],
        "expected_drugs": ["Lisinopril", "Amlodipine", "Hydrochlorothiazide"]
    },
    {
        "id": 2,
        "title": "Type 2 Diabetes Treatment",
        "prescription": "Metformin 500mg twice daily with meals, Gliclazide 80mg once daily before breakfast",
        "patient_age": 62,
        "conditions": ["diabetes"],
        "expected_drugs": ["Metformin", "Gliclazide"]
    },
    {
        "id": 3,
        "title": "Pain Management Protocol",
        "prescription": "Ibuprofen 400mg three times daily after meals, Acetaminophen 500mg every 6 hours as needed for pain",
        "patient_age": 45,
        "conditions": [],
        "expected_drugs": ["Ibuprofen", "Acetaminophen"]
    },
    {
        "id": 4,
        "title": "Anticoagulation Therapy",
        "prescription": "Warfarin 5mg once daily at bedtime, Aspirin 75mg once daily for cardioprotection",
        "patient_age": 68,
        "conditions": ["heart disease"],
        "expected_drugs": ["Warfarin", "Aspirin"]
    },
    {
        "id": 5,
        "title": "Complex Polypharmacy Case",
        "prescription": "Lisinopril 10mg daily, Atorvastatin 20mg at bedtime, Metformin 1000mg twice daily, Omeprazole 20mg daily, Levothyroxine 50mcg in the morning",
        "patient_age": 72,
        "conditions": ["hypertension", "diabetes", "heart disease"],
        "expected_drugs": ["Lisinopril", "Atorvastatin", "Metformin", "Omeprazole", "Levothyroxine"]
    }
]

DRUG_INFORMATION = {
    "lisinopril": {
        "class": "ACE Inhibitor",
        "indications": ["Hypertension", "Heart Failure", "Post-MI"],
        "common_doses": ["5mg", "10mg", "20mg", "40mg"],
        "frequency": "Once daily",
        "side_effects": ["Dry cough", "Hyperkalemia", "Angioedema"],
        "monitoring": ["Blood pressure", "Serum creatinine", "Potassium"],
        "contraindications": ["Pregnancy", "Angioedema history", "Bilateral renal artery stenosis"]
    },
    "amlodipine": {
        "class": "Calcium Channel Blocker",
        "indications": ["Hypertension", "Angina"],
        "common_doses": ["2.5mg", "5mg", "10mg"],
        "frequency": "Once daily",
        "side_effects": ["Peripheral edema", "Flushing", "Headache"],
        "monitoring": ["Blood pressure", "Heart rate", "Edema"],
        "contraindications": ["Severe aortic stenosis", "Cardiogenic shock"]
    },
    "metformin": {
        "class": "Biguanide",
        "indications": ["Type 2 Diabetes", "PCOS"],
        "common_doses": ["500mg", "850mg", "1000mg"],
        "frequency": "1-3 times daily with meals",
        "side_effects": ["GI upset", "Lactic acidosis (rare)", "B12 deficiency"],
        "monitoring": ["HbA1c", "Renal function", "B12 levels"],
        "contraindications": ["Severe renal impairment", "Metabolic acidosis"]
    },
    "warfarin": {
        "class": "Anticoagulant",
        "indications": ["Atrial fibrillation", "DVT/PE", "Mechanical heart valves"],
        "common_doses": ["1mg", "2mg", "5mg", "10mg"],
        "frequency": "Once daily",
        "side_effects": ["Bleeding", "Skin necrosis", "Purple toe syndrome"],
        "monitoring": ["INR", "Signs of bleeding", "Drug interactions"],
        "contraindications": ["Active bleeding", "Pregnancy", "Severe liver disease"]
    },
    "ibuprofen": {
        "class": "NSAID",
        "indications": ["Pain", "Inflammation", "Fever"],
        "common_doses": ["200mg", "400mg", "600mg"],
        "frequency": "3-4 times daily",
        "side_effects": ["GI bleeding", "Renal impairment", "Cardiovascular risk"],
        "monitoring": ["Renal function", "GI symptoms", "Blood pressure"],
        "contraindications": ["Active GI bleeding", "Severe heart failure", "Severe renal impairment"]
    }
}

AGE_SPECIFIC_DOSING = {
    "pediatric": {
        "age_range": "0-17 years",
        "special_considerations": [
            "Weight-based dosing often required",
            "Organ system immaturity affects drug metabolism",
            "Limited safety data for many medications",
            "Risk of off-label use"
        ],
        "contraindicated_drugs": ["Aspirin", "Fluoroquinolones", "Tetracyclines"]
    },
    "adult": {
        "age_range": "18-64 years",
        "special_considerations": [
            "Standard dosing applies",
            "Consider pregnancy/breastfeeding status",
            "Monitor for drug interactions"
        ]
    },
    "elderly": {
        "age_range": "65+ years",
        "special_considerations": [
            "Start low, go slow approach",
            "Increased risk of adverse effects",
            "Polypharmacy concerns",
            "Renal function decline",
            "Cognitive considerations"
        ],
        "high_risk_drugs": ["Warfarin", "Digoxin", "Lithium", "Phenytoin"]
    }
}

INTERACTION_MECHANISMS = {
    "pharmacokinetic": {
        "description": "Affects drug absorption, distribution, metabolism, or elimination",
        "examples": [
            "CYP enzyme inhibition/induction",
            "Protein binding displacement",
            "Renal clearance competition"
        ]
    },
    "pharmacodynamic": {
        "description": "Affects drug action at receptor or physiological level",
        "examples": [
            "Additive effects",
            "Antagonistic effects",
            "Synergistic effects"
        ]
    }
}