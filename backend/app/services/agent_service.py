import os
import re
import json
import logging
from typing import Tuple, Optional
from groq import Groq

from app.database.connection import SessionLocal
from app.services.memory_service import generate_memory_context, store_memory
from app.memory.hindsight_memory import save_memory, retrieve_memory
from app.rag.retriever import get_policy_answer
from app.services.order_service import get_order_status
from app.services.refund_service import get_refund_status

logger = logging.getLogger(__name__)

def get_groq_client() -> Optional[Groq]:
    """
    Initializes and returns the Groq client. Returns None if key is missing.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def call_groq(prompt: str, system_message: str = "You are a helpful assistant.") -> str:
    """
    Calls the Groq LLM with a prompt and system message using the Llama 3 model.
    Provides fallback behavior for local testing if the API key is not configured.
    """
    client = get_groq_client()
    if not client:
        return f"[Mock Groq Response] (GROQ_API_KEY is not configured)\nPrompt context: {prompt[:150]}..."

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
            temperature=0.2
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return f"Sorry, I encountered an error communicating with my language processor: {e}"

def detect_intent_and_ids(message: str) -> Tuple[str, Optional[int], Optional[int]]:
    """
    Detects user intent (POLICY, ORDER, REFUND, GENERAL) and extracts order/refund IDs.
    Uses LLM classification with a regex fallback.
    """
    client = get_groq_client()
    if not client:
        # Regex fallback for local development
        msg_lower = message.lower()
        order_match = re.search(r'\border\b.*?(\d+)', msg_lower)
        refund_match = re.search(r'\brefund\b.*?(\d+)', msg_lower)
        policy_keywords = ["policy", "shipping", "return", "faq", "delivery cost", "days", "postage"]
        
        if order_match:
            return "ORDER", int(order_match.group(1)), None
        elif refund_match:
            return "REFUND", None, int(refund_match.group(1))
        elif any(kw in msg_lower for kw in policy_keywords):
            return "POLICY", None, None
        return "GENERAL", None, None

    prompt = (
        "Classify the user query into one of these intents: POLICY, ORDER, REFUND, GENERAL.\n"
        "- POLICY: Questions about shipping rules, return periods, refund conditions, general company FAQs.\n"
        "- ORDER: Checking order status, delivery date, items in a specific order.\n"
        "- REFUND: Inquiries regarding refund status or refund amount.\n"
        "- GENERAL: Greetings, thanks, chit-chat, or general questions.\n\n"
        "Also extract order_id or refund_id as integers if mentioned (return null if not present).\n"
        "Return ONLY a raw JSON object with keys: 'intent', 'order_id', 'refund_id'.\n"
        f"Query: \"{message}\""
    )

    try:
        response = call_groq(prompt, system_message="You are a precise classifier. Return only valid JSON.")
        json_match = re.search(r'\{.*?\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            intent = data.get("intent", "GENERAL").upper()
            order_id = data.get("order_id")
            refund_id = data.get("refund_id")
            return intent, order_id, refund_id
    except Exception as e:
        logger.error(f"Error during intent classification: {e}")

    return "GENERAL", None, None

def generate_summary(message: str, response: str, intent: str) -> str:
    """
    Generates a concise one-sentence summary (max 15 words) of the conversation.
    """
    client = get_groq_client()
    if not client:
        return f"Discussed {intent.lower()} inquiry."

    prompt = (
        "Summarize this interaction in a single short sentence of less than 15 words.\n"
        f"User: {message}\n"
        f"Assistant: {response}"
    )
    try:
        summary = call_groq(prompt)
        return summary.strip().strip('"\'.')
    except Exception:
        return f"Interaction regarding {intent.lower()} info."

def process_user_message(user_id: int, message: str) -> str:
    """
    Processes user messages, manages agent logic routing, and updates user memory.
    """
    db = SessionLocal()
    try:
        # 1. Retrieve memory contexts
        db_context = generate_memory_context(db, user_id)
        hindsight_context = retrieve_memory(user_id)
        
        # Merge contexts
        context_parts = []
        if db_context:
            context_parts.append(f"Recent User Interactions:\n{db_context}")
        if hindsight_context:
            context_parts.append(f"Long-term User Memory:\n{hindsight_context}")
        memory_context = "\n\n".join(context_parts)

        # 2. Detect user intent and extract relevant identifiers
        intent, order_id, refund_id = detect_intent_and_ids(message)
        logger.info(f"User {user_id} message intent classified as {intent} (order_id={order_id}, refund_id={refund_id})")

        # 3. Route workflow based on intent
        if intent == "POLICY":
            # Retrieve RAG context
            policy_context = get_policy_answer(message)
            prompt = (
                f"User Message: {message}\n\n"
                f"User Memory Context:\n{memory_context}\n\n"
                f"Company Policy Information:\n{policy_context}\n\n"
                "Using the company policy details above, provide a precise and helpful response to the user. "
                "Keep previous user history in mind if applicable."
            )
            response = call_groq(prompt)

        elif intent == "ORDER":
            # Retrieve Order status
            order_details = None
            if order_id is not None:
                order = get_order_status(db, order_id)
                if order:
                    order_details = (
                        f"Order ID: {order.order_id}\n"
                        f"Product: {order.product_name}\n"
                        f"Status: {order.status}\n"
                        f"Delivery Date: {order.delivery_date}"
                    )
            
            if order_details:
                prompt = (
                    f"User Message: {message}\n\n"
                    f"User Memory Context:\n{memory_context}\n\n"
                    f"Order Information:\n{order_details}\n\n"
                    "Formulate a helpful and friendly response updating the user about their order details."
                )
            else:
                prompt = (
                    f"User Message: {message}\n\n"
                    f"User Memory Context:\n{memory_context}\n\n"
                    f"Order ID: {order_id}\n"
                    "No order details were found matching this ID. Inform the user politely and ask them to verify their order number."
                )
            response = call_groq(prompt)

        elif intent == "REFUND":
            # Retrieve Refund status
            refund_details = None
            if refund_id is not None:
                refund = get_refund_status(db, refund_id)
                if refund:
                    refund_details = (
                        f"Refund ID: {refund.refund_id}\n"
                        f"Order ID: {refund.order_id}\n"
                        f"Status: {refund.status}\n"
                        f"Amount: ${refund.amount}"
                    )
            
            if refund_details:
                prompt = (
                    f"User Message: {message}\n\n"
                    f"User Memory Context:\n{memory_context}\n\n"
                    f"Refund Information:\n{refund_details}\n\n"
                    "Formulate a helpful response explaining the status of the user's refund."
                )
            else:
                prompt = (
                    f"User Message: {message}\n\n"
                    f"User Memory Context:\n{memory_context}\n\n"
                    f"Refund ID: {refund_id}\n"
                    "No refund details were found matching this ID. Inform the user politely and ask them to double check."
                )
            response = call_groq(prompt)

        else:  # GENERAL
            prompt = (
                f"User Message: {message}\n\n"
                f"User Memory Context:\n{memory_context}\n\n"
                "Respond to the user's message in a helpful and customer-centric manner. "
                "Keep their memory context in mind to personalize the reply."
            )
            response = call_groq(prompt)

        # 4. Save memory updates asynchronously (after generating the response)
        try:
            # Store in Hindsight Memory SDK
            save_memory(user_id, message, response)
        except Exception as e:
            logger.error(f"Failed to save memory to Hindsight: {e}")
        
        try:
            # Store in local relational database
            summary = generate_summary(message, response, intent)
            store_memory(db, user_id, summary=summary, issue_type=intent)
        except Exception as e:
            logger.error(f"Failed to save memory to local database: {e}")

        return response

    finally:
        db.close()
