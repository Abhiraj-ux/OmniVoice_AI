import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    def __init__(self):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("DATABASE_COLLECTION", "accessibility_knowledge")
        self.user_profiles_collection = "user_profiles"
        
        if not self.url or not self.api_key:
            print("⚠️ Qdrant credentials missing. Skipping client initialization.")
            self.client = None
            self.embed_model = None
        else:
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
            self.embed_model = TextEmbedding()
            self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the target collections exist."""
        if not self.client: return
        target_collections = [self.collection_name, self.user_profiles_collection]
        try:
            existing = [c.name for c in self.client.get_collections().collections]
            for col in target_collections:
                if col not in existing:
                    self.client.create_collection(
                        collection_name=col,
                        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
                    )
                    print(f"✅ Created collection: {col}")
        except Exception as e:
            print(f"❌ Error ensuring collections: {e}")

    def search_knowledge(self, query, collection_name=None, limit=3):
        """Search for relevant civic schemas or documents."""
        if not self.client or not self.embed_model:
            return []
        
        target_collection = collection_name or self.collection_name
        query_vector = list(self.embed_model.embed([query]))[0].tolist()
        
        try:
            return self.client.search(
                collection_name=target_collection,
                query_vector=query_vector,
                limit=limit
            )
        except Exception:
            return [] # Collection might not exist

    def upsert_insight(self, topic, content, source="Global Web Research"):
        """Store a new learned insight into the vector database."""
        if not self.client or not self.embed_model:
            return False
        
        try:
            full_content = f"Topic: {topic}\nInsight: {content}"
            vector = list(self.embed_model.embed([full_content]))[0].tolist()
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "content": full_content,
                            "topic": topic,
                            "source": source,
                            "type": "learned_insight",
                            "timestamp": "2026-04-13" # Capturing the current "real-world" date
                        }
                    )
                ]
            )
            print(f"✨ Successfully vectorized insight about: {topic}")
            return True
        except Exception as e:
            print(f"❌ Failed to upsert insight: {e}")
            return False

    def store_session_summary(self, user_id, summary):
        """Store a high-level summary of a call for long-term user context."""
        if not self.client or not self.embed_model:
            return False
        
        try:
            vector = list(self.embed_model.embed([summary]))[0].tolist()
            self.client.upsert(
                collection_name=self.user_profiles_collection,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "user_id": user_id,
                            "summary": summary,
                            "type": "session_memory",
                            "timestamp": "2026-04-13"
                        }
                    )
                ]
            )
            print(f"🧠 Saved session memory for user: {user_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to store session summary: {e}")
            return False

# Global Instance
qdrant_service = QdrantService()
