import os
import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "user_profiles"
IDENTITY_FILE = "backend/data/identity.json"
USER_ID = "developer" # Default user ID for the personal identity

def ingest_identity():
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Error: QDRANT_URL or QDRANT_API_KEY not found in .env")
        return

    if not os.path.exists(IDENTITY_FILE):
        print(f"❌ Error: {IDENTITY_FILE} not found.")
        return

    with open(IDENTITY_FILE, 'r') as f:
        identity_data = json.load(f)

    # Convert dictionary to a searchable text block
    identity_text = f"User Identity Profile for {USER_ID}:\n"
    for kl, v in identity_data.items():
        identity_text += f"{kl.replace('_', ' ').capitalize()}: {v}\n"

    print(f"Ingesting identity for: {identity_data.get('full_name', USER_ID)}")

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    embed_model = TextEmbedding()

    # Ensure collection exists and create indexes
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")
        
    # Create indexes for optimized filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="user_id",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="type",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )

    # Explicitly clear old developer identity to avoid duplicates
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=USER_ID),
                ),
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(value="personal_identity"),
                )
            ]
        ),
    )

    # Embed and upsert
    vector = list(embed_model.embed([identity_text]))[0].tolist()
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "user_id": USER_ID,
                    "content": identity_text,
                    "type": "personal_identity",
                    "raw_data": identity_data,
                    "timestamp": "2026-04-13"
                }
            )
        ]
    )

    print(f"Successfully stored personal identity for {USER_ID} in Qdrant!")

if __name__ == "__main__":
    ingest_identity()
