import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("DATABASE_COLLECTION", "civic_knowledge")
        
        if not self.url or not self.api_key:
            print("⚠️ Qdrant credentials missing. Skipping client initialization.")
            self.client = None
        else:
            self.client = QdrantClient(url=self.url, api_key=self.api_key)

    def search_knowledge(self, query_vector, limit=3):
        """Search for relevant civic schemas or documents."""
        if not self.client:
            return []
        
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

# Global Instance
qdrant_service = QdrantService()
