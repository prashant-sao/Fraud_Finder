from application.agent.scam_checker import check_scam_database
from application.agent.rule_checker import check_red_flags
from application.agent.llm_analyzer import analyze_with_ollama
from application.agent.extract_utils import extract_email, extract_phone, extract_company_name, extract_website
from application.agent.scorer import calculate_risk_score
from application.agent.company_checker import check_company_legitimacy
import logging

logger = logging.getLogger(__name__)

class CorporateAgent:
    def __init__(self):
        # Initialize agents
        self.scam_checker = check_scam_database
        self.red_flag_checker = check_red_flags
        self.llm_analyzer = analyze_with_ollama
        self.company_legitimacy_checker = check_company_legitimacy

    def analyze_job_post(self, job_post: str):
        """Analyzes a job post using multiple agents and integrates the results."""
        
        try:
            # Extract key information
            email = extract_email(job_post)
            phone = extract_phone(job_post)
            company_name = extract_company_name(job_post)
            company_website = extract_website(job_post)

            # Perform scam check
            scam_result = self.scam_checker(email, phone)

            # Perform red flag check
            red_flags = self.red_flag_checker(job_post)

            # Perform LLM analysis
            llm_analysis = self.llm_analyzer(job_post)

            # Perform company legitimacy check
            company_legitimacy = self.company_legitimacy_checker(company_name, company_website)

            # Calculate risk score
            risk_score = calculate_risk_score(red_flags, llm_analysis, scam_result, company_legitimacy)

            # Compile the results
            result = {
                "scam_result": scam_result,
                "red_flags": red_flags,
                "llm_analysis": llm_analysis,
                "company_legitimacy": company_legitimacy,
                "risk_score": risk_score,
                "company_name": company_name,
                "company_website": company_website
            }

            return result
            
        except Exception as e:
            logger.error(f"Job post analysis error: {str(e)}")
            # Return safe defaults
            return {
                "scam_result": {"email_flagged": False, "phone_flagged": False},
                "red_flags": [],
                "llm_analysis": {"reasoning": "Analysis failed"},
                "company_legitimacy": {"website_exists": False, "linkedin_exists": False},
                "risk_score": 50,  # Medium risk as default
                "company_name": None,
                "company_website": None
            }