import os
import requests
import logging

logger = logging.getLogger(__name__)

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")

class HindsightMemorySDK:
    """
    A wrapper integrating the Hindsight API/SDK for managing conversation memories.
    """
    def __init__(self):
        self.api_key = HINDSIGHT_API_KEY
        self.base_url = HINDSIGHT_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def store_summary(self, user_id: str, summary: str) -> bool:
        """
        Stores a summary of the conversation in Hindsight memory.
        """
        if not self.api_key:
            logger.warning("HINDSIGHT_API_KEY is not set.")
            return False

        payload = {
            "user_id": user_id,
            "text": summary,
            "type": "summary"
        }
        
        try:
            # Assuming standard REST API endpoint structure for Hindsight
            response = requests.post(
                f"{self.base_url}/v1/memory", 
                json=payload, 
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error storing summary in Hindsight SDK: {str(e)}")
            return False

    def retrieve_latest_memories(self, user_id: str, limit: int = 5) -> list:
        """
        Retrieves the latest memory summaries for a given user_id.
        """
        if not self.api_key:
            logger.warning("HINDSIGHT_API_KEY is not set.")
            return []

        try:
            response = requests.get(
                f"{self.base_url}/v1/memory", 
                params={"user_id": user_id, "limit": limit, "sort": "desc"},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("memories", [])
        except Exception as e:
            logger.error(f"Error retrieving memories from Hindsight SDK: {str(e)}")
            return []

# Singleton instance for the application to use
hindsight_sdk = HindsightMemorySDK()
