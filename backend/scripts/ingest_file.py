import uuid
import os
import sys
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("DATABASE_COLLECTION", "accessibility_knowledge")

if not QDRANT_URL:
    print("[ERROR] QDRANT_URL not found in .env")
    sys.exit(1)

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
embed_model = TextEmbedding()

def chunk_text(text, chunk_size=600, overlap=100):
    """Slices text into overlapping chunks for better RAG context."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def ingest_file(file_path):
    print(f"[START] Processing: {file_path}")
    
    text = ""
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print("[ERROR] Unsupported file type. Use .pdf or .txt")
        return

    print(f"[INFO] Extracted {len(text)} characters. Chunking...")
    chunks = chunk_text(text)
    print(f"[INFO] Created {len(chunks)} shards.")

    # Embed and Upload
    vectors = list(embed_model.embed(chunks))
    
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector.tolist(),
            payload={
                "text": chunks[i],
                "source": os.path.basename(file_path),
                "type": "file_import"
            }
        )
        for i, vector in enumerate(vectors)
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"[SUCCESS] {os.path.basename(file_path)} is now in OmniVoice Memory!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/ingest_file.py <path_to_file>")
    else:
        ingest_file(sys.argv[1])
