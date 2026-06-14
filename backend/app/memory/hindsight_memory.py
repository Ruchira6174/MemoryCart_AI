import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Try to import Hindsight client from SDK
try:
    from hindsight_client import Hindsight
    HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")
    hindsight_client = Hindsight(base_url=HINDSIGHT_API_URL)
except ImportError:
    hindsight_client = None
    logger.warning("hindsight-client SDK not found. Falling back to local mock memory store.")

# Local in-memory dictionary acting as a fallback for development/testing
_mock_memory_store: Dict[int, List[str]] = {}

def save_memory(user_id: int, message: str, response: str) -> bool:
    """
    Stores a conversation message-response pair for a user in their memory bank.
    Integrates with Hindsight SDK, falling back to a local memory store on failure or missing SDK.
    """
    content = f"User: {message}\nAssistant: {response}"
    bank_id = f"user_{user_id}"

    # Try storing via Hindsight API SDK
    if hindsight_client is not None:
        try:
            hindsight_client.retain(bank_id=bank_id, content=content)
            return True
        except Exception as e:
            logger.error(f"Failed to retain memory in Hindsight: {e}. Falling back to mock store.")

    # Fallback to local in-memory store
    if user_id not in _mock_memory_store:
        _mock_memory_store[user_id] = []
    _mock_memory_store[user_id].append(content)
    return True

def retrieve_memory(user_id: int) -> str:
    """
    Retrieves a synthesized summary of previous conversation history for a user.
    Uses Hindsight reflect/recall API, falling back to local memory store formatting.
    """
    bank_id = f"user_{user_id}"

    # Try retrieving and reflecting via Hindsight API SDK
    if hindsight_client is not None:
        try:
            # Reflect analyzes memories to generate synthesized summaries/observations
            summary = hindsight_client.reflect(
                bank_id=bank_id,
                query="Provide a concise summary of the past conversations and what the user has asked or experienced."
            )
            if summary:
                return str(summary).strip()
        except Exception as e:
            logger.error(f"Failed to reflect memory using Hindsight: {e}.")
            try:
                # Fallback query using recall
                results = hindsight_client.recall(
                    bank_id=bank_id,
                    query="What did the user ask or experience in past conversations?"
                )
                if results:
                    return "\n".join([str(res).strip() for res in results])
            except Exception as re:
                logger.error(f"Failed to recall memory using Hindsight: {re}.")

    # Fallback retrieval from local mock store
    user_memories = _mock_memory_store.get(user_id, [])
    if not user_memories:
        return ""

    # Return the last 5 conversation pairs formatted as a summary context
    formatted_history = [f"- {m.replace(chr(10), ' | ')}" for m in user_memories[-5:]]
    return "Summary of past conversation history:\n" + "\n".join(formatted_history)
