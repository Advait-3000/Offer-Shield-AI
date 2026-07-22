# gemini_utils.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT

load_dotenv()

class GeminiHelper:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
    
    def extract_details(self, text: str) -> dict:
        """Extract structured info from offer text"""
        try:
            prompt = EXTRACTION_PROMPT.format(text=text[:3000])  # Truncate for API
            response = self.model.generate_content(prompt)
            
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response)
        except Exception as e:
            # Fallback extraction using regex
            return self._fallback_extraction(text)
    
    def verify_offer(self, extracted: dict) -> dict:
        """Verify offer and return risk assessment"""
        try:
            prompt = VERIFICATION_PROMPT.format(extracted=json.dumps(extracted, indent=2))
            response = self.model.generate_content(prompt)
            
            # Clean response
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            return json.loads(cleaned_response)
        except Exception as e:
            # Fallback verification
            return self._fallback_verification(extracted)
    
    def _fallback_extraction(self, text: str) -> dict:
        """Rule-based extraction fallback"""
        import re
        
        def find(pattern, default="Not Found"):
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else default
        
        return {
            "company_name": find(r"(?:Company|Organization|Firm):\s*(.+)", "Not Found"),
            "recruiter_name": find(r"(?:Recruiter|HR|Contact):\s*(.+)", "Not Found"),
            "recruiter_email": find(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Not Found"),
            "salary": find(r"(?:Salary|Stipend):\s*([\d,]+)", "Not Found"),
            "joining_date": find(r"(?:Joining|Start|Report)\s+Date:\s*([\d/ -]+)", "Not Mentioned"),
            "interview_mentioned": "Yes" if "interview" in text.lower() else "No",
            "payment_requested": "Yes" if any(word in text.lower() for word in ["fee", "payment", "deposit"]) else "No"
        }
    
    def _fallback_verification(self, extracted: dict) -> dict:
        """Rule-based verification fallback"""
        checks = []
        risk_score = 0
        
        # Check 1: Company legitimacy (simple check)
        if extracted.get("company_name") and extracted["company_name"] != "Not Found":
            checks.append({"check": "Company Legitimacy", "status": "✅", "message": "Company name identified"})
        else:
            checks.append({"check": "Company Legitimacy", "status": "❌", "message": "Company name not clearly mentioned"})
            risk_score += 20
        
        # Check 2: Email domain
        email = extracted.get("recruiter_email", "")
        if email and email != "Not Found":
            if any(domain in email.lower() for domain in ["gmail", "yahoo", "outlook", "hotmail"]):
                checks.append({"check": "Email Domain", "status": "❌", "message": "Personal email used (red flag)"})
                risk_score += 25
            else:
                checks.append({"check": "Email Domain", "status": "✅", "message": "Professional email domain"})
        else:
            checks.append({"check": "Email Domain", "status": "⚠️", "message": "Email not found"})
            risk_score += 10
        
        # Check 3: Interview process
        if extracted.get("interview_mentioned") == "Yes":
            checks.append({"check": "Interview Process", "status": "✅", "message": "Interview process mentioned"})
        else:
            checks.append({"check": "Interview Process", "status": "❌", "message": "No interview mentioned (suspicious)"})
            risk_score += 20
        
        # Check 4: Payment request
        if extracted.get("payment_requested") == "Yes":
            checks.append({"check": "Payment Request", "status": "❌", "message": "Payment requested before joining (BIG RED FLAG)"})
            risk_score += 35
        else:
            checks.append({"check": "Payment Request", "status": "✅", "message": "No payment requested"})
        
        # Check 5: Salary realism (simple check)
        salary = extracted.get("salary", "")
        if salary and salary != "Not Found":
            try:
                salary_num = int(re.sub(r'[^0-9]', '', salary))
                if salary_num > 1000000:  # Unrealistically high
                    checks.append({"check": "Salary Realistic", "status": "❌", "message": f"Salary {salary} seems unrealistically high"})
                    risk_score += 15
                else:
                    checks.append({"check": "Salary Realistic", "status": "✅", "message": f"Salary {salary} seems reasonable"})
            except:
                checks.append({"check": "Salary Realistic", "status": "⚠️", "message": "Salary format unclear"})
        else:
            checks.append({"check": "Salary Realistic", "status": "⚠️", "message": "Salary not mentioned"})
        
        # Determine risk level
        risk_level = "HIGH RISK" if risk_score >= 40 else "LOW RISK"
        
        # Generate conclusion
        if risk_level == "HIGH RISK":
            conclusion = "🚨 This offer shows multiple red flags including " + ", ".join([
                c["message"].lower() for c in checks if c["status"] == "❌"
            ][:2]) + ". We strongly recommend you DO NOT proceed with this offer. Always verify company details through official channels and NEVER pay money for a job."
        else:
            conclusion = "✅ This offer appears to be legitimate. However, we still recommend verifying the company website, connecting with the recruiter on LinkedIn, and checking with your college placement cell as a precaution."
        
        return {
            "verification_checks": checks,
            "risk_level": risk_level,
            "conclusion": conclusion
        }

    