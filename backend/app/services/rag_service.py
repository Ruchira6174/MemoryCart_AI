import logging
from app.rag.retriever import similarity_search

logger = logging.getLogger(__name__)

class RAGService:
    @staticmethod
    def get_relevant_context(query: str) -> list[str]:
        """
        Retrieves the top 3 relevant chunks from our ingested policies/FAQs
        to provide context for generation or answering queries.
        
        Args:
            query (str): The user query or search string.
            
        Returns:
            list[str]: A list containing the page_content of the top 3 chunks.
        """
        try:
            # Perform similarity search returning top 3 chunks as per requirements
            docs = similarity_search(query, k=3)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error retrieving RAG context for query '{query}': {str(e)}")
            return []
