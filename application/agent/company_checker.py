import requests
import logging

logger = logging.getLogger(__name__)

def check_website(url: str) -> bool:
    """Check if the website is valid."""
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False
    except Exception as e:
        logger.error(f"Website check error: {str(e)}")
        return False

def check_linkedin_page(company_name: str) -> bool:
    """Check if the company has a LinkedIn page."""
    if not company_name:
        return False
        
    # Clean company name for URL
    clean_name = company_name.lower().replace(' ', '-').replace('&', 'and')
    linkedin_url = f"https://www.linkedin.com/company/{clean_name}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(linkedin_url, headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False
    except Exception as e:
        logger.error(f"LinkedIn check error: {str(e)}")
        return False

def check_company_legitimacy(company_name: str, website_url: str) -> dict:
    """Check the legitimacy of a company by verifying its website and LinkedIn page."""
    legitimacy_result = {
        "website_exists": False,
        "linkedin_exists": False,
    }

    # Check if the website exists
    if website_url:
        legitimacy_result["website_exists"] = check_website(website_url)

    # Check if the LinkedIn page exists
    if company_name:
        legitimacy_result["linkedin_exists"] = check_linkedin_page(company_name)

    return legitimacy_result