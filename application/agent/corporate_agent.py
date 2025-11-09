# application/agent/corporate_agent.py

import logging
from application.agent.llm_analyzer import analyze_with_ollama

logger = logging.getLogger(__name__)

class CorporateAgent:
    """High-level wrapper for LLM-powered job post analysis."""

    def __init__(self):
        logger.info("CorporateAgent initialized using Ollama LLM.")

    def analyze_job_post(self, job_post: str):
        """Perform a detailed fraud analysis using the Ollama model."""
        try:
            result = analyze_with_ollama(job_post)
            logger.info(f"LLM analysis completed - Score: {result.get('risk_score')}, Verdict: {result.get('verdict')}")
            return result
        except Exception as e:
            logger.error(f"CorporateAgent analysis failed: {e}")
            return {
                "risk_score": 50,
                "risk_level": "Medium",
                "verdict": "unknown",
                "red_flags": ["LLM analysis failed"],
                "reasoning": "Fallback: unable to analyze post"
            }
