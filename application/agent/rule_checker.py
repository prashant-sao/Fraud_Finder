import re

def check_red_flags(text):
    """Check for red flags in job posting text"""
    flags = []
    
    # Communication platform red flags
    if "Telegram" in text or "WhatsApp" in text:
        flags.append("Asks to contact on Telegram/WhatsApp.")
    
    # Salary red flags
    if "no experience" in text.lower() and "high salary" in text.lower():
        flags.append("Unrealistic salary for no experience.")
    
    # Information request red flags
    if "send your details to" in text.lower():
        flags.append("Requests personal info upfront.")
    
    # Cryptocurrency red flags
    if "Bitcoin" in text or "crypto" in text.lower():
        flags.append("Mentions Bitcoin or crypto payments.")
    
    # Email domain red flags
    if re.search(r"\b(gmail\.com|yahoo\.com|outlook\.com)\b", text, re.IGNORECASE):
        flags.append("Uses free/public email instead of company domain.")
    
    # Unrealistic salary pattern
    salary_patterns = [
        r'\$\d{3,4}/week',  # $XXX/week
        r'\$\d{4,}/day',    # $XXXX/day
        r'earn \$\d{3,4}',  # earn $XXX
    ]
    
    for pattern in salary_patterns:
        if re.search(pattern, text):
            flags.append("Unrealistic salary offered (e.g., $3000/week)")
            break
    
    # Personal details request
    personal_details_pattern = r'(send\s+details|send\s+resume|contact\s+info|personal\s+information)'
    if re.search(personal_details_pattern, text, re.IGNORECASE):
        flags.append("Asking for personal details or resume upfront")
    
    # Suspicious domains
    suspicious_domains = ['.xyz', '.top', '.club', '.work', '.space', '.online', '.tk', '.ml']
    for domain in suspicious_domains:
        if domain in text:
            flags.append(f"Suspicious domain {domain} in website URL")
            break
    
    # Urgency tactics
    urgency_words = ['urgent', 'immediate', 'asap', 'hurry', 'limited time', 'act now']
    text_lower = text.lower()
    for word in urgency_words:
        if word in text_lower:
            flags.append("Uses urgency tactics to pressure quick decisions")
            break
    
    # Too good to be true offers
    if re.search(r'(work from home|easy money|no experience required.*high pay)', text, re.IGNORECASE):
        flags.append("Too good to be true work-from-home offer")
    
    return flags