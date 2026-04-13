# OmniVoice AI — Voice Agent for Accessibility & Societal Impact

> Built for Vapi + Qdrant | Multilingual | Low-Literacy Friendly | 5 Domains

---

## 📁 Project Structure

```
voice-agent/
├── system_prompt.md              ← Paste this into your Vapi Assistant settings
├── ingest_to_qdrant.py           ← Run this to load all KB into Qdrant
└── knowledge_base/
    ├── healthcare.json           ← 8 records: fever, dengue, Ayushman Bharat...
    ├── education.json            ← 7 records: NSP scholarships, Skill India...
    ├── public_services.json      ← 8 records: Aadhaar, ration card, RTI...
    ├── finance.json              ← 7 records: Jan Dhan, UPI, Mudra loan...
    └── agriculture.json          ← 8 records: PM-KISAN, MSP, KCC...
```

---

## 🚀 Setup

### 1. Start Qdrant (Docker)
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Or use Qdrant Cloud: https://cloud.qdrant.io (free tier available)

### 2. Install Python dependencies
```bash
pip install qdrant-client sentence-transformers
```

### 3. Ingest knowledge base
```bash
python ingest_to_qdrant.py
```
This creates 5 Qdrant collections and ingests all KB records with multilingual embeddings.

### 4. Configure Vapi
1. Go to https://dashboard.vapi.ai
2. Create a new Assistant
3. Paste the contents of `system_prompt.md` into the System Prompt field
4. Set voice settings: speed 0.9x, noise cancellation ON, silence timeout 8s
5. Connect your RAG tool / function calling to query Qdrant collections

---

## 🧠 Qdrant Collections

| Collection           | Domain          | Records |
|----------------------|-----------------|---------|
| `kb_healthcare`      | Healthcare      | 8       |
| `kb_education`       | Education       | 7       |
| `kb_public_services` | Public Services | 8       |
| `kb_finance`         | Finance         | 7       |
| `kb_agriculture`     | Agriculture     | 8       |

---

## 🔎 RAG Query Logic (Pseudo-code for Vapi Tool)

```javascript
// Vapi Tool: query_knowledge_base
async function queryKnowledgeBase(userQuery, detectedDomain) {
  const collectionMap = {
    healthcare:      "kb_healthcare",
    education:       "kb_education",
    public_services: "kb_public_services",
    finance:         "kb_finance",
    agriculture:     "kb_agriculture",
  };

  const collection = collectionMap[detectedDomain] || "kb_public_services";
  const embedding  = await embedText(userQuery);  // use same model as ingest

  const results = await qdrantClient.search({
    collection_name: collection,
    vector: embedding,
    limit: 3,
    score_threshold: 0.55,
  });

  return results.map(r => ({
    title:   r.payload.title,
    content: r.payload.content,
    source:  r.payload.source,
    score:   r.score,
  }));
}
```

---

## 🌐 Languages Supported
English, Hindi, Kannada, Tamil, Telugu, Bengali, Marathi, Gujarati

Embedding model: `paraphrase-multilingual-MiniLM-L12-v2` — natively multilingual, 50+ languages.

---

## 📞 Key Helpline Numbers (in system prompt)
| Service                  | Number              |
|--------------------------|---------------------|
| National Emergency       | 112                 |
| Ambulance                | 108                 |
| PM-JAY (Health)          | 14555               |
| Kisan (Agriculture)      | 1800-180-1551       |
| Cyber Crime / Fraud      | 1930                |
| Mental Health (iCall)    | 9152987821          |
| RTI Online               | rtionline.gov.in    |

---

## 🏆 Impact Domains
- **Healthcare**: First aid, maternal health, mental health, Ayushman Bharat
- **Education**: Scholarships, loans, vocational training, online learning
- **Public Services**: Aadhaar, ration card, housing, pensions, MGNREGA
- **Finance**: Zero-balance accounts, UPI, microloans, fraud prevention
- **Agriculture**: MSP, crop insurance, weather alerts, organic farming
