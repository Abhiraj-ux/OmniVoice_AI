import json
import os
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL     = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
VECTOR_SIZE    = 384   
KB_DIR         = Path(__file__).parent / "knowledge_base"

COLLECTION_MAP = {
    "healthcare":      "kb_healthcare",
    "education":       "kb_education",
    "public_services": "kb_public_services",
    "finance":         "kb_finance",
    "agriculture":     "kb_agriculture",
    "personal_profile": "kb_developer_profile",
}

client  = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
encoder = TextEmbedding()
print("[INFO] Starting Ingestion...")

def ensure_collection(collection_name: str):
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"  [CREATE] {collection_name}")

def ingest_file(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        records = json.load(f)
    if not records: return
    domain = records[0]["domain"]
    collection_name = COLLECTION_MAP.get(domain)
    if not collection_name: return
    ensure_collection(collection_name)
    points = []
    for rec in records:
        text_to_embed = f"{rec['title']}. {rec['content']} Tags: {', '.join(rec.get('tags', []))}"
        vector = list(encoder.embed([text_to_embed]))[0].tolist()
        point = PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, rec["id"])),
            vector=vector,
            payload={
                "doc_id":   rec["id"],
                "domain":   rec["domain"],
                "title":    rec["title"],
                "content":  rec["content"],
                "tags":     rec.get("tags", []),
                "language": rec.get("language", "en"),
                "source":   rec.get("source", ""),
            }
        )
        points.append(point)
    client.upsert(collection_name=collection_name, points=points)
    print(f"  [SUCCESS] {len(points)} points added to {collection_name}")

if __name__ == "__main__":
    json_files = sorted(KB_DIR.glob("*.json"))
    for filepath in json_files:
        print(f"[START] {filepath.name}")
        ingest_file(filepath)
    print("[FINAL] All knowledge domains are live.")
