import ollama
import logging

logger = logging.getLogger(__name__)

LLM_PROMPT_TEMPLATE = """
Analyze the following job posting for potential fraud indicators. 
Consider factors like:
- Unrealistic salary promises
- Urgency tactics
- Poor grammar/spelling
- Vague job descriptions
- Unusual payment methods
- Suspicious contact information

Rate the risk level as HIGH, MEDIUM, or LOW and provide reasoning.

Job posting:
{text}

Risk Assessment:
"""

def analyze_with_ollama(text):
    """Analyze text using Ollama LLM"""
    try:
        prompt = LLM_PROMPT_TEMPLATE.format(text=text)
        
        # Use Ollama API to send the prompt to the model
        response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        
        # Extract the reasoning from the response
        output = response["message"]["content"]
        return {"reasoning": output}
        
    except Exception as e:
        logger.error(f"LLM analysis error: {str(e)}")
        # Return default medium risk if LLM fails
        return {"reasoning": "medium risk - analysis service temporarily unavailable"}
