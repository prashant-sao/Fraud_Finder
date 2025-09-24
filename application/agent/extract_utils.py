import re
import spacy
import logging

logger = logging.getLogger(__name__)

# Load English NLP model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Company name extraction will be limited.")
    nlp = None

def extract_website(text):
    """Extract website URL from text"""
    # More comprehensive URL regex
    urls = re.findall(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?', text)
    if not urls:
        # Look for www domains
        urls = re.findall(r'www\.(?:[-\w.])+\.(?:[a-zA-Z]{2,4})', text)
        if urls:
            return 'https://' + urls[0]
    return urls[0] if urls else None

def extract_company_name(text):
    """Extract company name from text using NLP"""
    if not nlp:
        # Fallback: look for patterns like "at [Company]" or "join [Company]"
        patterns = [
            r'(?:at|join|with)\s+([A-Z][a-zA-Z\s&]+)(?:\s+(?:Inc|LLC|Corp|Ltd|Co)\.?)?',
            r'([A-Z][a-zA-Z\s&]+)(?:\s+(?:Inc|LLC|Corp|Ltd|Co)\.?)\s+is\s+hiring'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None
    
    try:
        doc = nlp(text)
        # Look for organizations, prioritize longer names
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        if orgs:
            # Return the longest organization name found
            return max(orgs, key=len)
        return None
    except Exception as e:
        logger.error(f"Company name extraction error: {str(e)}")
        return None

def extract_email(text: str) -> str:
    """Extract email from text"""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    # More comprehensive phone pattern
    phone_patterns = [
        r'\+?\d{1,4}[\s-]?\(?\d{2,4}\)?[\s-]?[\d\s-]{6,15}',  # International format
        r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',  # US format (XXX) XXX-XXXX
        r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',  # US format XXX-XXX-XXXX
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None