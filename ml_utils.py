# ml_utils.py

import json
import re

class MLPredictor:
    """
    ML Model Integration for Scam Detection
    Your ML teammate can replace this with actual model inference
    """
    
    def __init__(self):
        # Your ML teammate can load the trained model here
        # Example: self.model = joblib.load('scam_detector.pkl')
        pass
    
    def predict_risk(self, extracted_data: dict, verification_checks: list) -> dict:
        """
        Predict risk using ML model
        Returns: {"risk": "HIGH RISK" or "LOW RISK", "confidence": "High/Low/Medium"}
        """
        
        # ⚠️ THIS IS A DUMMY IMPLEMENTATION
        # Your ML teammate should replace this with actual model inference
        
        # Count red flags from verification checks
        red_flags = sum(1 for check in verification_checks if check["status"] == "❌")
        warnings = sum(1 for check in verification_checks if check["status"] == "⚠️")
        
        # Simple rule-based (replace with ML model)
        if red_flags >= 2:
            risk = "HIGH RISK"
            confidence = "High"
        elif red_flags == 1 and warnings >= 2:
            risk = "HIGH RISK"
            confidence = "Medium"
        else:
            risk = "LOW RISK"
            confidence = "High" if red_flags == 0 else "Medium"
        
        # Your ML teammate can use this extracted data for features:
        features = {
            "company_name": extracted_data.get("company_name", ""),
            "recruiter_email": extracted_data.get("recruiter_email", ""),
            "payment_requested": 1 if extracted_data.get("payment_requested") == "Yes" else 0,
            "interview_mentioned": 1 if extracted_data.get("interview_mentioned") == "Yes" else 0,
            "salary_amount": self._extract_salary_amount(extracted_data.get("salary", "")),
            "red_flags_count": red_flags
        }
        
        return {
            "risk": risk,
            "confidence": confidence,
            "features_used": features  # For transparency
        }
    
    def _extract_salary_amount(self, salary_str: str) -> int:
        """Extract numeric salary amount"""
        if not salary_str or salary_str == "Not Found":
            return 0
        numbers = re.findall(r'\d+', salary_str)
        return int(''.join(numbers)) if numbers else 0