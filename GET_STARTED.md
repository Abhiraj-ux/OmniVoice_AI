# Getting Started with CivicGuardian

## 1. Environment Setup
Fill in your API keys in the `.env` file (copy from `.env.example` if you haven't yet).
You need:
- `OPENAI_API_KEY`: For embeddings and LLM logic.
- `QDRANT_URL` & `QDRANT_API_KEY`: From your Qdrant Cloud dashboard.
- `VAPI_PRIVATE_KEY` & `VAPI_PUBLIC_KEY`: From your Vapi dashboard.

## 2. Ingest Impact Data
Provide the brain with knowledge. Run the following in your terminal:
```bash
cd backend
pip install -r requirements.txt
python scripts/ingest_data.py
```

## 3. Connect the Frontend
Open `frontend/script.js` and replace:
- `YOUR_VAPI_PUBLIC_KEY_HERE` with your public key.
- `YOUR_ASSISTANT_ID_HERE` with the ID of your created Vapi assistant.

## 4. Run the Server
Start the backend for webhooks:
```bash
python main.py
```
And open `frontend/index.html` in your browser to start calling!
