# prompts.py

EXTRACTION_PROMPT = """
You are an AI assistant that extracts structured information from internship/job offer letters.

Extract the following details from the given text:
1. Company Name
2. Recruiter Name
3. Recruiter Email
4. Salary/Stipend amount
5. Joining Date
6. Is Interview Mentioned? (Yes/No)
7. Is Payment Requested? (Yes/No)

Return ONLY a JSON object with these exact keys:
{
    "company_name": "",
    "recruiter_name": "",
    "recruiter_email": "",
    "salary": "",
    "joining_date": "",
    "interview_mentioned": "",
    "payment_requested": ""
}

Text to analyze:
{text}
"""

VERIFICATION_PROMPT = """
You are a cybersecurity expert analyzing an internship/job offer for scams.

Based on the extracted details, check these verification points:
1. Is the company legitimate? (Check if company name seems real)
2. Is the recruiter email from a legitimate domain? (not gmail/yahoo)
3. Is the salary realistic for the role? (not extremely high)
4. Is there a proper interview process mentioned?
5. Is payment requested before joining? (BIG RED FLAG)

For each verification point, return:
- status: "✅" or "❌"
- message: brief explanation

Also provide:
- risk_level: "HIGH RISK" or "LOW RISK" only
- conclusion: A clear, friendly message explaining WHY it's fraud or safe (2-3 sentences)

Return ONLY JSON:
{
    "verification_checks": [
        {"check": "Company Legitimacy", "status": "✅", "message": "..."},
        {"check": "Email Domain", "status": "✅", "message": "..."},
        {"check": "Salary Realistic", "status": "✅", "message": "..."},
        {"check": "Interview Process", "status": "✅", "message": "..."},
        {"check": "Payment Request", "status": "✅", "message": "..."}
    ],
    "risk_level": "HIGH RISK",
    "conclusion": "This offer appears to be..."
}

Extracted Details:
{extracted}
"""