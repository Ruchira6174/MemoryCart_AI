"""
agent_service.py — Core agent logic for MemoryCart AI.

Routing pipeline:
  1. Retrieve memory context (DB + Hindsight)
  2. Rule-based intent detection  (no LLM call — fast, zero-cost)
  3. Extract IDs via regex
  4. Validate IDs are present before DB lookups
  5. Gate RAG: never call Groq with empty policy context
  6. Call Groq ONCE for final response generation
  7. Persist memory (DB + Hindsight)
"""

import os
import re
import logging
from typing import Tuple, Optional

from groq import Groq

from app.database.connection import SessionLocal
from app.services.memory_service import generate_memory_context, store_memory
from app.memory.hindsight_memory import save_memory, retrieve_memory
from app.services.rag_service import query_policy
from app.services.order_service import get_order_status
from app.services.refund_service import get_refund_status

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared system prompt — used for every Groq response call
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are MemoryCart AI, an e-commerce customer support assistant.\n\n"
    "Rules:\n"
    "- Never invent policies.\n"
    "- Never invent order information.\n"
    "- Never invent refund information.\n"
    "- Use memory when relevant.\n"
    "- Be concise, helpful, and professional."
)

# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------

def get_groq_client() -> Optional[Groq]:
    """Initialise and return the Groq client. Returns None if key is missing."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def call_groq(prompt: str, system_message: str = SYSTEM_PROMPT) -> str:
    """
    Call the Groq LLM for final response generation.
    Uses the shared system prompt by default.
    Includes timeout + exception handling — never crashes the request.
    """
    client = get_groq_client()
    if not client:
        logger.warning("GROQ_API_KEY not configured — returning mock response.")
        return (
            "I'm currently running in limited mode. "
            "Please configure GROQ_API_KEY for full AI responses."
        )

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            temperature=0.2,
            timeout=30,  # seconds — prevents indefinite blocking
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return (
            "I'm having trouble connecting to my AI processor right now. "
            "Please try again in a moment."
        )


# ---------------------------------------------------------------------------
# Rule-based intent detection — zero LLM calls, instant, deterministic
# ---------------------------------------------------------------------------

# Keyword groups (evaluated top-to-bottom; first match wins)
_ORDER_KEYWORDS = [
    "order", "track order", "delivery status", "order status",
    "where is my", "shipped", "dispatched", "package",
]
_REFUND_KEYWORDS = [
    "refund", "refund status", "refund id", "money back",
    "reimbursement", "return my money",
]
_POLICY_KEYWORDS = [
    "return policy", "shipping policy", "shipping cost", "shipping time",
    "shipping fee", "faq", "returns", "how long does", "how many days",
    "postage", "delivery cost", "exchange policy", "cancellation policy",
    "warranty", "terms and conditions", "store policy",
]


def detect_intent_and_ids(message: str) -> Tuple[str, Optional[int], Optional[int]]:
    """
    Classify user intent and extract numeric IDs using pure regex/keyword rules.
    No LLM calls — fast, deterministic, zero API cost.

    Returns:
        (intent, order_id, refund_id)
        intent is one of: "ORDER", "REFUND", "POLICY", "GENERAL"
    """
    msg_lower = message.lower()

    # Extract numeric IDs anywhere in the message
    # Prefer patterns like "order 1001", "order #1001", "order id 1001"
    order_id_match = re.search(
        r'order\s*(?:id\s*|#\s*)?(\d+)', msg_lower
    )
    refund_id_match = re.search(
        r'refund\s*(?:id\s*|#\s*)?(\d+)', msg_lower
    )

    order_id: Optional[int] = int(order_id_match.group(1)) if order_id_match else None
    refund_id: Optional[int] = int(refund_id_match.group(1)) if refund_id_match else None

    # Determine intent — refund check before order to avoid misclassification
    # (a refund message may also contain the word "order")
    if any(kw in msg_lower for kw in _REFUND_KEYWORDS):
        return "REFUND", order_id, refund_id

    if any(kw in msg_lower for kw in _ORDER_KEYWORDS):
        return "ORDER", order_id, refund_id

    if any(kw in msg_lower for kw in _POLICY_KEYWORDS):
        return "POLICY", None, None

    return "GENERAL", None, None


# ---------------------------------------------------------------------------
# Summary generator (used for DB memory storage)
# ---------------------------------------------------------------------------

def generate_summary(message: str, response: str, intent: str) -> str:
    """
    Generate a concise summary for memory storage using a deterministic template.
    Zero Groq API calls — keeps the pipeline at exactly ONE LLM call per message.
    """
    # Truncate to keep summaries readable and DB-friendly
    msg_preview = message[:80].replace("\n", " ")
    return f"{intent}: {msg_preview}"


# ---------------------------------------------------------------------------
# Main agent entrypoint
# ---------------------------------------------------------------------------

def process_user_message(user_id: int, message: str) -> str:
    """
    End-to-end message processing pipeline:
      Memory retrieval → Intent detection → ID validation →
      Tool execution → RAG / DB lookup → Groq response → Memory storage
    """
    db = SessionLocal()
    try:
        # ------------------------------------------------------------------ #
        # 1. Retrieve memory contexts
        # ------------------------------------------------------------------ #
        db_context = ""
        hindsight_context = ""

        try:
            db_context = generate_memory_context(db, user_id)
        except Exception as e:
            logger.error(f"Failed to retrieve DB memory for user {user_id}: {e}")

        try:
            hindsight_context = retrieve_memory(user_id)
        except Exception as e:
            logger.error(f"Failed to retrieve Hindsight memory for user {user_id}: {e}")

        context_parts = []
        if db_context:
            context_parts.append(f"Recent User Interactions:\n{db_context}")
        if hindsight_context:
            context_parts.append(f"Long-term User Memory:\n{hindsight_context}")
        memory_context = "\n\n".join(context_parts)

        # ------------------------------------------------------------------ #
        # 2. Rule-based intent detection (no Groq call)
        # ------------------------------------------------------------------ #
        intent, order_id, refund_id = detect_intent_and_ids(message)
        logger.info(
            f"User {user_id} | intent={intent} | "
            f"order_id={order_id} | refund_id={refund_id}"
        )

        # ------------------------------------------------------------------ #
        # 3. Route by intent
        # ------------------------------------------------------------------ #
        response: str

        if intent == "ORDER":
            # Phase 2: Validate ID presence before any lookup
            if order_id is None:
                response = (
                    "Please provide your order ID so I can check its status. "
                    "You can find it in your confirmation email (e.g. 'order 1001')."
                )
            else:
                order = get_order_status(db, order_id)
                if order:
                    order_details = (
                        f"Order ID: {order.order_id}\n"
                        f"Product: {order.product_name}\n"
                        f"Status: {order.status}\n"
                        f"Delivery Date: {order.delivery_date}"
                    )
                    prompt = (
                        f"User Message: {message}\n\n"
                        f"User Memory Context:\n{memory_context}\n\n"
                        f"Order Information:\n{order_details}\n\n"
                        "Provide a helpful and friendly response about the order details above."
                    )
                    response = call_groq(prompt)
                else:
                    prompt = (
                        f"User Message: {message}\n\n"
                        f"User Memory Context:\n{memory_context}\n\n"
                        f"No order was found with Order ID: {order_id}.\n"
                        "Politely inform the user and ask them to verify their order number."
                    )
                    response = call_groq(prompt)

        elif intent == "REFUND":
            # Phase 2: Validate ID presence before any lookup
            if refund_id is None:
                response = (
                    "Please provide your refund ID so I can check its status. "
                    "Your refund ID was included in the refund confirmation email."
                )
            else:
                refund = get_refund_status(db, refund_id)
                if refund:
                    refund_details = (
                        f"Refund ID: {refund.refund_id}\n"
                        f"Order ID: {refund.order_id}\n"
                        f"Status: {refund.status}\n"
                        f"Amount: ${refund.amount:.2f}"
                    )
                    prompt = (
                        f"User Message: {message}\n\n"
                        f"User Memory Context:\n{memory_context}\n\n"
                        f"Refund Information:\n{refund_details}\n\n"
                        "Provide a helpful response explaining the refund status above."
                    )
                    response = call_groq(prompt)
                else:
                    prompt = (
                        f"User Message: {message}\n\n"
                        f"User Memory Context:\n{memory_context}\n\n"
                        f"No refund was found with Refund ID: {refund_id}.\n"
                        "Politely inform the user and ask them to double-check their refund ID."
                    )
                    response = call_groq(prompt)

        elif intent == "POLICY":
            # Phase 3: Gate Groq call — never answer policy questions without context
            policy_context = query_policy(message)
            if not policy_context or not policy_context.strip():
                logger.warning(f"RAG returned no context for policy question: {message!r}")
                response = (
                    "I could not find policy information related to your question. "
                    "Please contact our support team directly for detailed policy guidance."
                )
            else:
                prompt = (
                    f"User Message: {message}\n\n"
                    f"User Memory Context:\n{memory_context}\n\n"
                    f"Company Policy Information:\n{policy_context}\n\n"
                    "Using ONLY the policy information above, provide a precise and helpful "
                    "response. Do not invent or extrapolate beyond the provided policy text."
                )
                response = call_groq(prompt)

        else:  # GENERAL
            prompt = (
                f"User Message: {message}\n\n"
                f"User Memory Context:\n{memory_context}\n\n"
                "Respond to the user's message in a helpful and customer-centric manner. "
                "Personalise the reply using memory context where relevant."
            )
            response = call_groq(prompt)

        # ------------------------------------------------------------------ #
        # 4. Persist memory (both Hindsight and DB)
        # ------------------------------------------------------------------ #
        try:
            save_memory(user_id, message, response)
        except Exception as e:
            logger.error(f"Failed to save Hindsight memory for user {user_id}: {e}")

        try:
            summary = generate_summary(message, response, intent)
            store_memory(db, user_id, summary=summary, issue_type=intent)
        except Exception as e:
            logger.error(f"Failed to save DB memory for user {user_id}: {e}")

        return response

    finally:
        db.close()
