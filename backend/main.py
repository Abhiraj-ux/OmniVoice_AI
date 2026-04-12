from fastapi import FastAPI, Request
from backend.services.qdrant_service import qdrant_service
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from googlesearch import search
from dotenv import load_dotenv
import uvicorn
import os
import uuid

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("DATABASE_COLLECTION", "accessibility_knowledge")

# Shared Services
app = FastAPI(title="OmniVoice AI Backend")
embed_model = TextEmbedding()
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

@app.get("/")
def health_check():
    return {"status": "healthy", "agent": "OmniVoice Premium"}

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {"status": "error", "message": "Invalid JSON"}
    
    message = payload.get("message", {})
    
    if message.get("type") == "tool-call":
        tool_call = message.get("toolCall", {})
        func_name = tool_call.get("function", {}).get("name")
        params = tool_call.get("function", {}).get("arguments", {})
        
        # 🟢 Tool 1: Multi-Domain Knowledge Base Search
        if func_name == "get_knowledge_base":
            query = params.get("query", "general help")
            # We'll search across all available KB collections
            collections = ["kb_healthcare", "kb_finance", "kb_agriculture", "kb_education", "kb_public_services", "accessibility_knowledge"]
            
            all_results = []
            for col in collections:
                try:
                    query_vector = list(embed_model.embed([query]))[0]
                    # Note: We'll use the client directly for multi-collection flexibility
                    results = client.search(
                        collection_name=col,
                        query_vector=query_vector.tolist(),
                        limit=2
                    )
                    for r in results:
                        all_results.append(f"[{col.upper()}]: {r.payload.get('content', r.payload.get('text', ''))}")
                except Exception:
                    continue # Skip if collection doesn't exist yet
            
            context = "\n".join(all_results)
            return {
                "results": [
                    {
                        "toolCallId": tool_call.get("id"),
                        "result": f"Internal memory context: {context}"
                    }
                ]
            }
        
        # 🔵 Tool 2: Web Search & Self-Learning
        if func_name == "web_search":
            query = params.get("query", "latest news")
            print(f"🌍 Researching via Global Web: {query}")
            
            search_results = []
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=10))
                    for r in results:
                        search_results.append({
                            "title": r['title'],
                            "description": r['body'],
                            "url": r['href']
                        })
            except Exception as e:
                print(f"⚠️ Search error: {e}")
            
            search_context = "\n".join([f"{r['title']}: {r['description']}" for r in search_results])

            # --- DYNAMIC SELF-LEARNING ---
            try:
                if search_context:
                    content_to_save = f"Topic: {query}\nDetails: {search_context[:1000]}"
                    vector = list(embed_model.embed([content_to_save]))[0]
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[
                            models.PointStruct(
                                id=str(uuid.uuid4()),
                                vector=vector.tolist(),
                                payload={
                                    "content": content_to_save,
                                    "source": f"Global Web Research: {query}",
                                    "type": "learned_insight"
                                }
                            )
                        ]
                    )
            except Exception: pass
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.get("id"),
                        "result": f"Latest Web Research: {search_context[:2000]}"
                    }
                ]
            }

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
