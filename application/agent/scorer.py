def calculate_risk_score(flags, llm_output, scam_check_result, legitimacy_result):
    """Calculate overall risk score based on all analysis results"""
    
    # Red flags score (0-100)
    red_flag_score = min(len(flags) * 15, 100)

    # LLM Score based on reasoning (0-40)
    llm_score = 0
    reasoning = llm_output.get("reasoning", "").lower()
    if "high" in reasoning:
        llm_score = 40
    elif "medium" in reasoning:
        llm_score = 25
    elif "low" in reasoning:
        llm_score = 10

    # Scam contact database score (0-100)
    scam_contact_score = 0
    if scam_check_result.get("email_flagged"):
        scam_contact_score += 50
    if scam_check_result.get("phone_flagged"):
        scam_contact_score += 50
    scam_contact_score = min(scam_contact_score, 100)

    # Company legitimacy score (0-100, inverse logic: missing info = higher risk)
    legitimacy_score = 100
    if legitimacy_result.get("website_exists"):
        legitimacy_score -= 40
    if legitimacy_result.get("linkedin_exists"):
        legitimacy_score -= 40
    legitimacy_score = max(0, legitimacy_score)

    # Final weighted score
    total_score = (
        red_flag_score * 0.25 +
        llm_score * 0.30 +
        scam_contact_score * 0.20 +
        legitimacy_score * 0.25
    )

    # Apply floor if LLM risk is high
    if "high" in reasoning:
        total_score = max(60, total_score)

    return round(total_score)