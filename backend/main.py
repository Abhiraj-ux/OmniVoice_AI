from fastapi import FastAPI, Request
from backend.services.qdrant_service import qdrant_service
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from duckduckgo_search import DDGS
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
# qdrant_service is already imported and initialized with its own client and embed_model

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
            # List of all domain collections plus the dynamic vault
            # List of all domain collections plus the dynamic vault and user profiles
            collections = ["kb_healthcare", "kb_education", "kb_agriculture", "kb_finance", "kb_public_services", "accessibility_knowledge", "user_profiles"]
            
            all_results = []
            for col in collections:
                results = qdrant_service.search_knowledge(query, collection_name=col, limit=2)
                for r in results:
                    source = r.payload.get('source', col.upper())
                    content = r.payload.get('content', r.payload.get('text', r.payload.get('summary', 'No content')))
                    all_results.append(f"[{source}]: {content}")
            
            context = "\n".join(all_results)
            return {
                "results": [
                    {
                        "toolCallId": tool_call.get("id"),
                        "result": f"Internal memory context: {context if all_results else 'No direct match in local memory. Use web_search for updated 2026 data.'}"
                    }
                ]
            }
        
        # 🔵 Tool 2: Web Search & Self-Learning (Updated to 2026 Today)
        if func_name == "web_search":
            query = params.get("query", "latest news")
            print(f"🌍 Researching via Global Web: {query}")
            
            search_results = []
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=12))
                    for r in results:
                        search_results.append({
                            "title": r['title'],
                            "description": r['body'],
                            "url": r['href']
                        })
            except Exception as e:
                print(f"⚠️ Search error: {e}")
            
            search_context = "\n".join([f"{r['title']}: {r['description']}" for r in search_results])

            # --- DYNAMIC SELF-LEARNING (Real-time Storage) ---
            if search_results:
                summary_to_store = f"Results for '{query}': {search_context[:1500]}"
                qdrant_service.upsert_insight(topic=query, content=summary_to_store)
            
            return {
                "results": [
                    {
                        "toolCallId": tool_call.get("id"),
                        "result": f"Latest Web Research (Knowledge Status: Today, April 2026): {search_context[:3000]}"
                    }
                ]
            }

    # 🟣 Message Type 2: Session End & Learning
    if message.get("type") == "end-of-call-report":
        summary = message.get("summary", "No summary provided")
        call_id = payload.get("call", {}).get("id", "unknown_call")
        customer_number = payload.get("call", {}).get("customer", {}).get("number", "guest")
        
        print(f"🏁 Call Ended: {call_id}. Summarizing for user {customer_number}...")
        qdrant_service.store_session_summary(user_id=customer_number, summary=summary)

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
