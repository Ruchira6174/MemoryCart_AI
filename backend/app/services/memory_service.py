import logging
from app.memory.hindsight_memory import hindsight_sdk

logger = logging.getLogger(__name__)

class MemoryService:
    @staticmethod
    def save_conversation_summary(user_id: int, full_chat: list) -> bool:
        """
        Converts a full chat into a summary and stores it in Hindsight.
        Fulfills the requirement: "Store summaries instead of full chats"
        """
        # Logic to create a summary instead of full chat
        # In a real app, you'd pass full_chat to an LLM (like Groq) to generate this summary.
        summary = MemoryService._generate_summary_from_chat(full_chat)
        
        success = hindsight_sdk.store_summary(user_id=str(user_id), summary=summary)
        
        if success:
            logger.info(f"Successfully stored conversation summary for user {user_id}")
        else:
            logger.error(f"Failed to store conversation summary for user {user_id}")
            
        return success

    @staticmethod
    def get_latest_memories(user_id: int, limit: int = 5) -> list:
        """
        Retrieves the latest memories/summaries for the user.
        Fulfills the requirement: "Retrieve memory by user_id" and "Return latest memories"
        """
        logger.info(f"Retrieving latest memories for user {user_id}")
        memories = hindsight_sdk.retrieve_latest_memories(user_id=str(user_id), limit=limit)
        return memories

    @staticmethod
    def _generate_summary_from_chat(full_chat: list) -> str:
        """
        Helper function to summarize the chat. 
        Placeholder for an LLM call that condenses the conversation.
        """
        if not full_chat:
            return "Empty conversation."
            
        # Example naive summary extraction
        return f"Conversation summary covering {len(full_chat)} messages."
