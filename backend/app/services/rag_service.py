"""
rag_service.py — Service-layer facade for the RAG (Retrieval-Augmented Generation) pipeline.

This module exposes a clean, service-layer interface that the agent and any
future API endpoints can call without depending directly on the RAG internals.
"""
import logging
from app.rag.retriever import get_policy_answer

logger = logging.getLogger(__name__)

def query_policy(question: str) -> str:
    """
    Retrieve relevant policy context for a given question using the RAG pipeline.

    Args:
        question: Natural language question from the user.

    Returns:
        Formatted policy context string, or an empty string if no match found.
    """
    try:
        context = get_policy_answer(question)
        if not context:
            logger.info("RAG retriever returned no context for question: %s", question)
            return ""
        return context
    except Exception as e:
        logger.error("RAG pipeline error: %s", e)
        return ""
