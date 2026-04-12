import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

# Sample data representing diverse domains
SAMPLE_KNOWLEDGE = [
    {
        "title": "Universal Healthcare Rights",
        "content": "Emergency care is a fundamental right. Any hospital must stabilize a patient regardless of their ability to pay.",
        "category": "Healthcare"
    },
    {
        "title": "Low-Barrier Banking",
        "content": "Basic savings accounts can be opened with a thumbprint. No minimum balance is required for accessibility accounts.",
        "category": "Finance"
    },
    {
        "title": "Digital Literacy Resources",
        "content": "Voice-guided tutorials are available at every community center to help users navigate essential digital services.",
        "category": "Education"
    }
]

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
# Using FastEmbed for local, free, high-quality embeddings (Open Source)
embed_model = TextEmbedding() 
COLLECTION_NAME = os.getenv("DATABASE_COLLECTION", "accessibility_knowledge")

def setup_knowledge_base():
    """Initializes the Qdrant collection and ingests sample impact data."""
    print(f"[START] Initializing collection: {COLLECTION_NAME}")
    
    # Create collection (FastEmbed vectors are typically 384 dimensions)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )
    
    documents = [item['content'] for item in SAMPLE_KNOWLEDGE]
    print(f"[INFO] Generating local embeddings for {len(documents)} items...")
    
    # Batch generate embeddings locally for free
    vectors = list(embed_model.embed(documents))
    
    points = [
        models.PointStruct(
            id=i,
            vector=vector.tolist(),
            payload=SAMPLE_KNOWLEDGE[i]
        )
        for i, vector in enumerate(vectors)
    ]
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("[SUCCESS] Open Source Knowledge Base Setup Complete!")

if __name__ == "__main__":
    if not os.getenv("QDRANT_URL"):
        print("❌ Error: Please set QDRANT_URL in your .env file first.")
    else:
        setup_knowledge_base()
