# Deployment Troubleshooting Guide

## Error: "DeploymentNotFound" - Embedding Model

### Problem
```
Embedding error: Error code: 404 - {'error': {'code': 'DeploymentNotFound', 'message': 'The API deployment for this resource does not exist...'}}
```

### Root Cause
The application is deployed on **Render free tier (512MB RAM)**, which is too small to load the local `BAAI/bge-large-en-v1.5` embedding model (~400MB). To work around this, the app uses **Azure OpenAI embeddings** instead, but the required deployment doesn't exist yet.

---

## Solution: Deploy Embedding Model in Azure OpenAI

### Step 1: Go to Azure OpenAI Studio
1. Navigate to: https://oai.azure.com/portal
2. Select your Azure OpenAI resource

### Step 2: Create Embedding Deployment
1. Click **Deployments** in the left sidebar
2. Click **+ Create new deployment**
3. Fill in the form:
   - **Model**: `text-embedding-3-small`
   - **Deployment name**: `text-embedding-3-small`
   - **Model version**: Latest available
   - **Dimensions**: `1024` (⚠️ IMPORTANT - must match Pinecone index)
   - **Tokens per Minute Rate Limit**: Set as desired (e.g., 350K)

4. Click **Create**
5. Wait ~1 minute for deployment

### Step 3: Verify Deployment
1. In Deployments tab, confirm you see:
   - `Llama-4-Maverick-17B-128E-Instruct-FP8` (for LLM/OCR)
   - `text-embedding-3-small` (for embeddings) ✅ NEW

### Step 4: Restart Your Application
- **Render**: Will auto-restart on next request
- **Local**: Restart uvicorn server

---

## Alternative Solution: Use Existing Deployment

If you already have a different embedding model deployed in Azure, you can use it instead:

### Option A: Set Environment Variable
Add to your `.env` or Render environment variables:
```bash
AZURE_EMBEDDING_MODEL=your-existing-embedding-deployment-name
AZURE_EMBEDDING_DIMS=1024  # Must be 1024 to match Pinecone
```

### Option B: Supported Models
Any of these work (with `dimensions=1024`):
- `text-embedding-3-small` (recommended - cheapest, fastest)
- `text-embedding-3-large`
- `text-embedding-ada-002` (legacy, no dimensions parameter - won't work)

---

## Memory Constraints

### Why Not Use Local Model?
The `BAAI/bge-large-en-v1.5` model requires:
- **Model size**: ~400MB
- **Runtime overhead**: ~100MB
- **Total**: ~500MB+ (exceeds Render free tier limit)

### Render Free Tier Limits
- **RAM**: 512MB max
- **Solution**: Use Azure OpenAI API (no local model loading)

### If You Have Paid Hosting (1GB+ RAM)
You can use the local model by editing `app/main.py`:

```python
from sentence_transformers import SentenceTransformer

# Initialize at startup
embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")

def get_embedding(text: str) -> List[float]:
    return embedding_model.encode(text, show_progress_bar=False).tolist()
```

**Benefits**:
- No Azure API calls for embeddings
- Exact same model as ingestion
- Lower latency

**Tradeoffs**:
- Requires 1GB+ RAM
- Slower startup time (~10 seconds)

---

## Verification

### Test Embedding Endpoint
```bash
# Check if deployment exists
curl -X POST "https://YOUR-RESOURCE.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2024-08-01-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR-API-KEY" \
  -d '{"input": "test", "dimensions": 1024}'
```

**Expected Response**:
```json
{
  "data": [{"embedding": [0.123, -0.456, ...], "index": 0}],
  "model": "text-embedding-3-small",
  "usage": {"prompt_tokens": 1, "total_tokens": 1}
}
```

### Test LLM Endpoint After Fix
```bash
curl -X POST "https://socar-hackathon.onrender.com/llm" \
  -H "Content-Type: application/json" \
  -d '{"question": "SOCAR haqqında məlumat verin"}'
```

**Expected**: No embedding errors, proper answer with sources

---

## Cost Implications

### Azure OpenAI Embeddings Pricing (text-embedding-3-small)
- **Cost**: $0.02 per 1M tokens (~$0.00000002 per query)
- **Typical query**: 10-50 tokens = $0.000001 (negligible)

### vs. Local Model
- **Cost**: $0 (but requires paid hosting with more RAM)
- **Hosting cost**: Render 1GB plan = $7/month

**Recommendation**: Use Azure embeddings on free tier, only switch to local if you already have paid hosting.

---

## Still Having Issues?

### Check Logs
```bash
# Render
render logs --tail 100

# Local
# Logs appear in terminal where you ran uvicorn
```

**Look for**:
```
❌ EMBEDDING ERROR: Deployment 'text-embedding-3-small' not found in Azure OpenAI
```

### Common Issues
1. **Wrong deployment name**: Check `AZURE_EMBEDDING_MODEL` env var
2. **Deployment still creating**: Wait 1-2 minutes after creating
3. **Wrong API version**: Use `2024-08-01-preview` or later
4. **Dimensions mismatch**: MUST be 1024 (Pinecone index requirement)

---

## Environment Variables Reference

```bash
# Required for LLM/OCR
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Required for embeddings (NEW)
AZURE_EMBEDDING_MODEL=text-embedding-3-small  # Your deployment name
AZURE_EMBEDDING_DIMS=1024  # Must match Pinecone

# Required for vector DB
PINECONE_API_KEY=<your-key>
PINECONE_INDEX_NAME=hackathon
```

---

**Last Updated**: December 14, 2025
**Status**: ✅ Fixed in app/main.py with better error messages
