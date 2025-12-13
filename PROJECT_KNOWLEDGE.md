# SOCAR Hackathon Project - Essential Knowledge Base

## Project Overview
**Purpose**: Document processing system for SOCAR historical oil & gas documents
**Goal**: OCR + RAG chatbot system for hackathon submission
**Scoring**: OCR Quality (50%) + LLM Quality (30%) + Architecture (20%)

---

## Critical Requirements

### API Endpoints (Must Have)
1. **POST /ocr** - PDF text extraction with image detection
2. **POST /llm** - RAG-based question answering

### Response Formats (Exact Specifications)

#### /ocr Response
```json
[
  {
    "page_number": 1,
    "MD_text": "Extracted text content...\n\n![Image](document_name.pdf/page_1/image_1)\n\n"
  }
]
```

**Key Points**:
- List of dictionaries (NOT nested object with "pages" field)
- Only two keys: `page_number` (int) and `MD_text` (str)
- Images referenced inline in MD_text as markdown path: `![Image](document_name.pdf/page_X/image_Y)`
- Path format: `{pdf_filename}/{page_folder}/{image_name}`
- NO separate "images" field
- NO base64 encoding - just simple path-like text references
- Only add image markdown when images actually exist on page

#### /llm Response
```json
{
  "answer": "Response text...",
  "sources": [
    {
      "pdf_name": "document_06.pdf",
      "page_number": 3,
      "content": "Relevant excerpt..."
    }
  ]
}
```

---

## Technology Stack

### 1. OCR (50% of score)
**Model**: Azure Document Intelligence API
- Endpoint: `prebuilt-read`
- Provider: Azure AI Services
- Performance: 92.79% CSR, 55.59% WSR
- Features: Multi-language (Azerbaijani, Russian, English), Cyrillic preservation, handwriting recognition

**Why Azure**:
- Tesseract achieved only 25% CSR (4x worse)
- Enterprise-grade accuracy
- Native Cyrillic support

**Configuration**:
```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

client = DocumentAnalysisClient(
    endpoint=azure_openai_endpoint,
    credential=AzureKeyCredential(api_key)
)
```

### 2. Embeddings
**Model**: `BAAI/bge-large-en-v1.5`
- Dimensions: 1024
- Library: sentence-transformers
- Purpose: Convert text chunks to vectors for semantic search

### 3. Vector Database
**Service**: Pinecone Cloud
- Index name: Configurable (e.g., "socar-documents")
- Dimensions: 1024 (must match embedding model)
- Metric: Cosine similarity
- Region: AWS us-east-1

**Alternative**: ChromaDB (local, good for development)

### 4. LLM (30% of score)
**Model**: `Llama-4-Maverick-17B-128E-Instruct-FP8`
- Provider: Azure OpenAI (or compatible endpoint)
- Parameters:
  - Temperature: 0.2 (factual, deterministic)
  - Max Tokens: 1000
  - Top-k documents: 3
- **Important**: Use this exact model name for open-source architecture points

### 5. Web Framework
**Framework**: FastAPI
- Async support
- Auto-generated docs at /docs
- File upload support (multipart/form-data)

### 6. Image Extraction
**Library**: PyMuPDF (fitz)
- Purpose: Detect images in PDFs
- Method: `page.get_images()`
- **Important**: Don't save images to disk, just reference them

---

## Environment Variables (.env)

```bash
# Azure AI Services
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Pinecone (if using)
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=socar-documents
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Application
API_HOST=0.0.0.0
API_PORT=8000
```

---

## RAG Pipeline Architecture

```
User Query
    ↓
1. Embed Query (BAAI/bge-large-en-v1.5)
    ↓
2. Search Vector DB (Cosine similarity, top 3 docs)
    ↓
3. Retrieve Relevant Chunks
    ↓
4. Build Context (3 documents × 600 chars)
    ↓
5. LLM Generation (Llama-4-Maverick-17B)
    ↓
Response with Citations
```

### Chunking Strategy
- Chunk size: 600 characters
- Overlap: 100 characters
- Preserves context across chunks
- **Important**: Only store extracted TEXT in vector database, NOT image markdown references
- Strip out image markdown (`![Image](...)`) before ingestion
- Images are only for OCR endpoint response, not for RAG

---

## Key Features & Requirements

### Cyrillic Support
- **Critical**: OCR must preserve Cyrillic alphabet (Russian text stays in Cyrillic)
- Don't transliterate Russian → Latin
- Azure Document Intelligence handles this natively

### Image Handling
- **Method**: Detect images using PyMuPDF
- **Format**: Path-like references: `document_name.pdf/page_X/image_Y`
- **Markdown**: `![Image](document_name.pdf/page_1/image_1)`
- **Path Structure**: `{pdf_filename}/{page_folder}/{image_name}`
- **Important**:
  - NO file saving
  - NO base64 encoding
  - Only add markdown when images exist
  - Check `if image_list:` before adding
  - Include full PDF filename in path

### OCR vs Vector Database (Critical Distinction)
**OCR Endpoint (`/ocr`)**:
- Returns text WITH image markdown references
- Format: `![Image](document.pdf/page_1/image_1)`
- Purpose: Show complete document structure to user

**Vector Database Ingestion**:
- Store ONLY text content, NO image references
- Strip out all `![Image](...)` markdown before adding to vector DB
- Purpose: Enable semantic search on text only
- Image markdown would pollute search results

**Example**:
```python
# OCR Response (with images)
MD_text = "Oil reserves...\n\n![Image](doc.pdf/page_1/image_1)\n\nTotal production..."

# Vector DB ingestion (text only)
import re
text_only = re.sub(r'!\[Image\]\([^)]+\)', '', MD_text)
# Result: "Oil reserves...\n\nTotal production..."
vector_db.add(text_only)
```

### Public Access
- Use ngrok for public endpoint
- Command: `ngrok http 8000`
- Free tier is sufficient
- Save the URL for hackathon submission

---

## Project Structure

```
SOCAR_Hackathon/
├── src/
│   ├── api/
│   │   └── main.py          # FastAPI app with /ocr and /llm endpoints
│   ├── ocr/
│   │   ├── processor.py     # Main OCR interface
│   │   └── azure_ocr.py     # Azure Document Intelligence implementation
│   ├── vectordb/
│   │   ├── pinecone_store.py # Pinecone operations
│   │   └── chroma_store.py   # ChromaDB alternative
│   ├── llm/
│   │   └── chat.py          # LLM integration with RAG
│   └── config.py            # Pydantic settings
├── data/
│   ├── pdfs/                # Input PDFs
│   └── processed/           # Processed data
├── run.py                   # Entry point
├── requirements.txt
├── .env
└── docker-compose.yml       # Optional
```

---

## Implementation Guidelines

### OCR Endpoint Implementation
```python
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    # 1. Read PDF bytes
    pdf_bytes = await file.read()
    pdf_filename = file.filename  # e.g., "document_06.pdf"

    # 2. Process with Azure Document Intelligence
    # - Extract text page by page
    # - Detect images with PyMuPDF
    # - Create path-like references: pdf_filename/page_X/image_Y
    # - Embed image references in MD_text

    # 3. Example of adding image reference
    # for each image detected on page 1:
    #   md_text += f"\n\n![Image]({pdf_filename}/page_1/image_1)\n\n"

    # 4. Return list of dicts
    return [
        {"page_number": 1, "MD_text": "text..."},
        {"page_number": 2, "MD_text": "text..."}
    ]
```

### LLM Endpoint Implementation
```python
@app.post("/llm")
async def llm_endpoint(messages: List[Dict]):
    # 1. Get last user message
    user_query = messages[-1]["content"]

    # 2. Generate embedding
    query_embedding = embed_model.encode(user_query)

    # 3. Search vector DB (top 3)
    results = vector_db.search(query_embedding, top_k=3)

    # 4. Build context from results
    context = "\n\n".join([doc["content"] for doc in results])

    # 5. Create prompt with context
    prompt = f"Context:\n{context}\n\nQuestion: {user_query}"

    # 6. Call LLM
    response = llm_client.chat(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000
    )

    # 7. Return answer with sources
    return {
        "answer": response.content,
        "sources": [
            {
                "pdf_name": doc["metadata"]["pdf_name"],
                "page_number": doc["metadata"]["page_number"],
                "content": doc["content"][:200]
            }
            for doc in results
        ]
    }
```

---

## Critical Dos and Don'ts

### ✅ DO
- Use exact model names: `Llama-4-Maverick-17B-128E-Instruct-FP8`
- Return exact response formats as specified
- Preserve Cyrillic text from OCR
- Only add image markdown when images exist
- Include source citations in LLM responses
- Use temperature 0.2 for factual answers
- Chunk documents at 600 chars with 100 overlap

### ❌ DON'T
- Change response format (no extra fields or nesting)
- Use base64 for images
- Save images to disk
- Transliterate Cyrillic to Latin
- Add image markdown when no images exist
- Use GPT models (use Llama for open-source points)
- Skip error handling

---

## Testing Commands

### Test OCR
```bash
curl -X POST http://localhost:8000/ocr \
  -F "file=@document.pdf"
```

### Test LLM
```bash
curl -X POST http://localhost:8000/llm \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "What is SOCAR?"}]'
```

### Test with ngrok
```bash
# Replace localhost with ngrok URL
curl -X POST https://your-url.ngrok-free.dev/llm \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "Test question"}]'
```

---

## Common Issues & Solutions

### Issue: Tesseract poor performance
**Solution**: Use Azure Document Intelligence (92.79% vs 25% CSR)

### Issue: Images bloating response
**Solution**: Don't use base64, use path-like text references: `document_name.pdf/page_1/image_1`

### Issue: Wrong response format
**Solution**: Return list directly, not `{"pages": [...]}`

### Issue: LLM taking too long
**Solution**:
- Limit to top 3 documents
- Use temperature 0.2
- Cap max_tokens at 1000

### Issue: Cyrillic not preserved
**Solution**: Azure handles this natively, ensure proper encoding throughout pipeline

---

## Performance Targets

- **OCR**: ~10-15 seconds for 12-page PDF
- **LLM**: ~3-5 seconds per query
- **Total RAG pipeline**: ~6-7 seconds (embedding + search + generation)

---

## Dependencies (requirements.txt essentials)

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Azure AI
azure-ai-formrecognizer==3.3.2
openai==1.3.0

# PDF Processing
PyMuPDF==1.23.8

# Vector DB & Embeddings
pinecone-client==3.0.0
sentence-transformers>=2.5.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
loguru==0.7.2
```

---

## Deployment Checklist

1. ✅ Set environment variables in .env
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Configure Azure Document Intelligence endpoint
4. ✅ Set up Pinecone index (1024 dimensions, cosine metric)
5. ✅ Ingest PDF documents into vector DB
6. ✅ Start FastAPI server: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
7. ✅ Start ngrok: `ngrok http 8000`
8. ✅ Test both endpoints
9. ✅ Verify Cyrillic preservation
10. ✅ Check image references in OCR output

---

## Scoring Optimization

### OCR Quality (50%)
- Azure Document Intelligence ✅
- Multi-language support ✅
- 92.79% CSR ✅
- Image detection ✅

### LLM Quality (30%)
- Open-source model (Llama) ✅
- RAG with 3-doc retrieval ✅
- Source citations ✅
- Contextual accuracy ✅

### Architecture (20%)
- Cloud vector DB (Pinecone) ✅
- Production-ready (FastAPI) ✅
- Open-source LLM ✅
- Modern stack ✅

---

## Quick Start from Scratch

1. Create project structure (see above)
2. Copy .env template and fill in credentials
3. Install dependencies
4. Implement /ocr endpoint with Azure Document Intelligence
5. Implement /llm endpoint with RAG pipeline
6. Set up vector database (Pinecone or ChromaDB)
7. Ingest PDF documents
8. Test locally
9. Deploy with ngrok
10. Submit hackathon URL

---

**Last Updated**: 2025-12-13
**Model**: Llama-4-Maverick-17B-128E-Instruct-FP8
**OCR**: Azure Document Intelligence (92.79% CSR)
**Vector DB**: Pinecone (1,241 chunks from 28 PDFs)
