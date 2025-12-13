# SOCAR Document Processing System - Architecture

## System Components

### 1. OCR (Optical Character Recognition)
**Model**: Azure Document Intelligence (`prebuilt-read`)
**NOT** Llama-4-Maverick (LLM is for answer generation, not OCR)

**Performance**:
- ✅ **92.79% Character Success Rate (CSR)**
- ✅ **55.59% Word Success Rate (WSR)**
- ✅ Significantly better than Tesseract (25% CSR, 21% WSR)

**Features**:
- ✅ Multi-language support (Azerbaijani, Russian, English)
- ✅ **Cyrillic alphabet PRESERVED** (Russian text stays in Cyrillic as-is)
- ✅ **Image detection** (lightweight references via PyMuPDF)
- ✅ Handwriting recognition
- ✅ Table detection

**Location**: `src/ocr/azure_ocr.py`

**Output Format**:
```json
[
  {
    "page_number": 1,
    "MD_text": "Text content with image references...\n\n![Image](document_page_1_image_1)\n\n"
  }
]
```

**Image Handling**:
- Images detected and referenced inline in MD_text (not saved to disk)
- Format: `![Image](document_page_X_image_Y)`
- Simple lightweight references, no base64, no file storage
- No separate "images" field - everything in MD_text
- Only adds image markdown when images actually exist on page

---

### 2. Embeddings (Vector Database Ingestion)
**Model**: `BAAI/bge-large-en-v1.5`
**Dimensions**: 1024 (matches Pinecone index)
**Purpose**: Converts text chunks into numerical vectors for semantic search

**Location**: `src/vectordb/pinecone_store.py:28`

```python
self.embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
self.embedding_dimension = 1024
```

**Process**:
1. Text chunks (600 chars, 100 overlap) → Embeddings (1024-dim vectors)
2. Upload to Pinecone cloud vector database
3. Enable semantic search (finds similar content)

---

### 3. Vector Database
**Service**: Pinecone (Cloud)
**Index**: `hackathon`
**Configuration**:
- Dimensions: 1024
- Metric: Cosine similarity
- Cloud: AWS us-east-1
- Type: Dense vectors
- Capacity: On-demand

**Location**: `src/vectordb/pinecone_store.py`

**Stats**:
- Total Documents: 1,241 chunks
- Source PDFs: 28 documents
- Embedding Model: BAAI/bge-large-en-v1.5

---

### 4. LLM (Answer Generation)
**Model**: `Llama-4-Maverick-17B-128E-Instruct-FP8` (Open-source)
**Purpose**: Generates contextual answers based on retrieved documents
**Provider**: Azure OpenAI

**Location**: `src/config.py:31`

```python
llm_model = "Llama-4-Maverick-17B-128E-Instruct-FP8"
```

**Parameters**:
- Temperature: 0.2 (deterministic, factual answers)
- Max Tokens: 1000
- Top-k Documents: 3 (from Pinecone)

---

## RAG Pipeline Flow

```
User Query
    ↓
1. Generate Query Embedding (BAAI/bge-large-en-v1.5)
    ↓
2. Search Pinecone (Cosine similarity, top 3 docs)
    ↓
3. Retrieve Relevant Chunks
    ↓
4. Build Context (3 documents × 600 chars)
    ↓
5. LLM Generation (Llama-4-Maverick-17B)
    ↓
Response with Citations
```

**Average Response Time**: 6.7 seconds
- Embedding generation: ~0.5s
- Pinecone search: ~1.0s
- LLM generation: ~3.2s
- Network overhead: ~2.0s

---

## Cyrillic Support

**OCR Output** (Cyrillic preserved):
```markdown
# Добыча нефти в Азербайджане

Южно-Каспийский бассейн...
```

**Chatbot** (Optional Azerbaijani conversion):
- OCR: **Cyrillic preserved** (requirement)
- Chatbot answers: Can be Azerbaijani alphabet (your choice)

---

## Image Detection

**Method**: PyMuPDF (fitz)
**Format**: Simple text references (not saved to disk)
**Included in**: OCR endpoint `/ocr`

**Example Response**:
```json
[
  {
    "page_number": 1,
    "MD_text": "Oil exploration map...\n\n![Image](document_06_page_1_image_1)\n\n"
  }
]
```

**Key Features**:
- Lightweight: No file storage, no base64 encoding
- Smart: Only adds image markdown when images exist
- Clean: Simple references like `document_page_1_image_1`

---

## API Endpoints

### 1. `POST /ocr` - PDF Processing
Extract text and detect images from PDF

**Request**:
```bash
curl -X POST http://localhost:8000/ocr \
  -F "file=@document.pdf"
```

**Response**:
```json
[
  {
    "page_number": 1,
    "MD_text": "Нефтяные месторождения...\n\n![Image](document_page_1_image_1)\n\n"
  }
]
```

### 2. `POST /llm` - RAG Chatbot
Ask questions about documents

**Request**:
```bash
curl -X POST http://localhost:8000/llm \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "What is SOCAR?"}]'
```

**Response**:
```json
{
  "answer": "SOCAR (State Oil Company of Azerbaijan Republic)...",
  "sources": [
    {
      "pdf_name": "document_06.pdf",
      "page_number": 3,
      "content": "SOCAR operates in..."
    }
  ]
}
```

---

## Model Summary

| Component | Model/Service | Purpose |
|-----------|--------------|---------|
| **OCR** | Azure Document Intelligence | Extract text + detect images (92.79% CSR, Cyrillic preserved) |
| **Embeddings** | BAAI/bge-large-en-v1.5 (1024-dim) | Convert text → vectors for search |
| **Vector DB** | Pinecone (AWS us-east-1) | Store & search 1,241 document chunks |
| **LLM** | Llama-4-Maverick-17B-128E-Instruct-FP8 | Generate contextual answers (Open-source) |

---

## Scoring Criteria Optimization

### OCR Quality (50%)
- ✅ Multi-language (Azerbaijani, Russian, English)
- ✅ **High accuracy: 92.79% CSR, 55.59% WSR**
- ✅ Cyrillic preservation (as required)
- ✅ Image detection (lightweight references)
- ✅ Azure Document Intelligence (enterprise-grade OCR)

### LLM Quality (30%)
- ✅ **Llama-4-Maverick-17B-128E-Instruct-FP8** (Open-source model)
- ✅ RAG with 3-document retrieval
- ✅ Source citations
- ✅ Contextual accuracy

### Architecture (20%)
- ✅ Cloud vector database (Pinecone)
- ✅ Production-ready (Docker, FastAPI)
- ✅ Open-source LLM (Llama-4-Maverick)
- ✅ Modern stack (Pinecone, sentence-transformers)

---

## Public Access

**ngrok URL**: `https://healthy-carolin-noncontagiously.ngrok-free.dev`

**Test Query**:
```bash
curl -X POST https://healthy-carolin-noncontagiously.ngrok-free.dev/llm \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "Что такое СОКАР?"}]'
```
**Expected**: Answer in Russian/Azerbaijani with source citations

---

## Repository
**GitHub**: https://github.com/Ismat-Samadov/SOCAR_Hackathon
**Stack**: Python 3.10, FastAPI, Pinecone, Azure AI, Docker
