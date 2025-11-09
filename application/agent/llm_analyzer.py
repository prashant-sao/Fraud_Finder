import ollama
import json
import logging

logger = logging.getLogger(__name__)

LLM_PROMPT_TEMPLATE = """
You are an AI assistant that detects fraudulent job postings.

Analyze the following job posting for potential fraud indicators.
Consider:
- Unrealistic salary or perks
- Urgency or pressure tactics
- Poor grammar or vague job roles
- Requests for payment or personal info
- Suspicious or missing company details

Return your response STRICTLY in the following JSON format:

{{
  "risk_score": <integer between 0 and 100>,
  "risk_level": "<Low|Medium|High>",
  "verdict": "<legitimate|fraudulent>",
  "red_flags": [<list of short risk indicators>],
  "reasoning": "<one-sentence summary>"
}}

Job Posting:
{text}
"""

def analyze_with_ollama(text):
    """Analyze job post text using Ollama LLM and return structured result."""
    try:
        prompt = LLM_PROMPT_TEMPLATE.format(text=text)
        
        # Query Ollama locally (make sure Ollama is running)
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        
        # Extract the model’s response text
        output_text = response["message"]["content"].strip()
        
        # Try to extract JSON safely even if the model adds extra text
        try:
            json_start = output_text.find('{')
            json_end = output_text.rfind('}') + 1
            json_text = output_text[json_start:json_end]
            result = json.loads(json_text)
        except Exception as parse_err:
            logger.warning(f"Failed to parse structured JSON from LLM output. Raw text: {output_text[:200]}...")
            result = {
                "risk_score": 50,
                "risk_level": "Medium",
                "verdict": "unknown",
                "red_flags": ["Unclear LLM output"],
                "reasoning": output_text
            }
        
        # Ensure default keys exist
        result.setdefault("risk_score", 50)
        result.setdefault("risk_level", "Medium")
        result.setdefault("verdict", "unknown")
        result.setdefault("red_flags", [])
        result.setdefault("reasoning", "No reasoning provided")

        return result

    except Exception as e:
        logger.error(f"LLM analysis error: {str(e)}")
        return {
            "risk_score": 50,
            "risk_level": "Medium",
            "verdict": "unknown",
            "red_flags": ["⚠️ LLM service unavailable"],
            "reasoning": "Fallback: LLM failed to analyze post."
        }
