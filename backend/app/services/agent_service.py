import os
import json
import logging
from sqlalchemy.orm import Session
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Import services
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.services.order_service import get_order_by_id
from app.services.refund_service import get_refund_by_id

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

class AgentService:
    @staticmethod
    def process_message(db: Session, user_id: int, message: str) -> str:
        """
        Process a user message through the full AI workflow.
        """
        # 1. Retrieve Hindsight Memory
        memories = MemoryService.get_latest_memories(user_id=user_id, limit=5)
        
        # Depending on how the Hindsight API returns data, we parse out the text.
        # Often it's a list of dictionaries with a 'text' or 'content' key.
        if memories and isinstance(memories[0], dict):
            memory_context = "\n".join([m.get("text", "") or m.get("content", "") for m in memories])
        elif memories:
            memory_context = "\n".join([str(m) for m in memories])
        else:
            memory_context = "No prior memory available."

        # 2. Detect Intent
        intent_data = AgentService._detect_intent(message, memory_context)
        intent = intent_data.get("intent", "general")
        extracted_id = intent_data.get("id")

        # 3. Tool Routing based on Intent
        tool_context = ""
        if intent == "policy":
            rag_chunks = RAGService.get_relevant_context(message)
            tool_context = "Policy Info:\n" + "\n---\n".join(rag_chunks)
            
        elif intent == "order" and extracted_id:
            try:
                order = get_order_by_id(db, int(extracted_id))
                if order:
                    tool_context = f"Order found: Product '{order.product_name}', Status: '{order.status}', Delivery: '{order.delivery_date}'"
                else:
                    tool_context = f"Order #{extracted_id} not found."
            except Exception as e:
                logger.error(f"Failed to retrieve order: {e}")
                tool_context = "Could not retrieve order details due to an error."
                
        elif intent == "refund" and extracted_id:
            try:
                refund = get_refund_by_id(db, int(extracted_id))
                if refund:
                    tool_context = f"Refund found: Status: '{refund.status}', Amount: '${refund.amount}'"
                else:
                    tool_context = f"Refund #{extracted_id} not found."
            except Exception as e:
                logger.error(f"Failed to retrieve refund: {e}")
                tool_context = "Could not retrieve refund details due to an error."
        else:
            tool_context = "No specific system tool was queried."

        # 4. Groq Response Generation
        final_response = AgentService._generate_response(message, memory_context, tool_context)

        # 5. Store Memory
        # Store a summary of this exact interaction
        interaction_summary = f"User asked: {message} | Agent replied: {final_response}"
        MemoryService.save_conversation_summary(user_id=user_id, full_chat=[interaction_summary])

        return final_response

    @staticmethod
    def _detect_intent(message: str, memory_context: str) -> dict:
        """
        Uses Groq to classify the intent of the user message.
        Expected intents: 'policy', 'order', 'refund', 'general'.
        """
        system_prompt = (
            "You are an intent classification engine. "
            "Analyze the user's message and output a JSON object with exactly two keys:\n"
            "- 'intent': must be one of ['policy', 'order', 'refund', 'general']\n"
            "- 'id': integer ID if an order number or refund ID is mentioned, otherwise null.\n\n"
            "Return ONLY valid JSON. Do not include markdown syntax, backticks, or any other text."
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {memory_context}\n\nMessage: {message}"}
                ],
                model=GROQ_MODEL,
                temperature=0.0,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting if model disobeys
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
                
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            return {"intent": "general", "id": None}

    @staticmethod
    def _generate_response(message: str, memory_context: str, tool_context: str) -> str:
        """
        Uses Groq to generate the final response leveraging context.
        """
        system_prompt = (
            "You are a helpful customer support AI for MemoryCart AI. "
            "Use the provided past memory context and the retrieved system tool context to accurately answer the user's query. "
            "Be polite, concise, and helpful.\n\n"
            f"--- Past Memory Context ---\n{memory_context}\n\n"
            f"--- Retrieved Tool Context ---\n{tool_context}"
        )

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                model=GROQ_MODEL,
                temperature=0.5,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I'm currently experiencing technical difficulties processing your request. Please try again later."
