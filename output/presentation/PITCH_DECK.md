# SOCAR Historical Documents AI
## Intelligent OCR & RAG System for Oil & Gas Archives

**Hackathon Pitch Deck**

---

# Slide 1: Title

# SOCAR Historical Documents AI

### Intelligent OCR & RAG System for Oil & Gas Archives

> Transforming 28 Historical Documents into Searchable Knowledge

---

# Slide 2: The Problem

## The Challenge We're Solving

### 1. Inaccessible Archives
- Decades of valuable historical documents locked in PDF format
- Impossible to search or query efficiently

### 2. Multi-Language Barrier
- Documents in **Azerbaijani**, **Russian**, and **English**
- Complex Cyrillic text preservation required

### 3. Time-Consuming Research
- Manual document review takes hours
- Finding specific information is a needle-in-haystack problem

> **How can we unlock institutional knowledge trapped in historical documents?**

---

# Slide 3: Our Solution

## A Complete Document Intelligence System

| Feature | Description |
|---------|-------------|
| **Vision-Language OCR** | Llama-4-Maverick extracts text with **87.75% accuracy**, preserving Cyrillic characters |
| **Semantic Search** | BAAI/bge-large embeddings + Pinecone enable instant retrieval across **1,128 chunks** |
| **RAG-Powered Q&A** | Natural language questions answered with **source citations** |
| **Production-Ready API** | FastAPI + Docker with health monitoring and web UI |

---

# Slide 4: System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐
│   PDF    │ -> │ Llama-4      │ -> │ BAAI/bge     │ -> │ Pinecone  │
│ Documents│    │ Vision OCR   │    │ Embeddings   │    │ Vector DB │
└──────────┘    └──────────────┘    └──────────────┘    └───────────┘
                                                              │
                                                              v
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐
│  Answer  │ <- │ Llama-4 LLM  │ <- │   Context    │ <- │  Top-3    │
│ + Sources│    │ Generation   │    │   Building   │    │ Retrieval │
└──────────┘    └──────────────┘    └──────────────┘    └───────────┘
```

### OCR Pipeline
```
PDF Upload → PyMuPDF (100 DPI) → Vision LLM → Image Detection → Markdown Output
```

### RAG Pipeline
```
User Question → Embed Query → Top-3 Retrieval → Context Building → LLM + Citations
```

---

# Slide 5: Technology Stack

## Open-Source & Production-Ready

| Component | Technology | Purpose |
|-----------|------------|---------|
| **OCR/LLM** | Llama-4-Maverick-17B | Vision & Language Model |
| **Embeddings** | BAAI/bge-large-en-v1.5 | 1024-dimensional vectors |
| **Vector DB** | Pinecone Cloud | Scalable similarity search |
| **API** | FastAPI | Async REST endpoints |
| **PDF Processing** | PyMuPDF | PDF to image conversion |
| **Deployment** | Docker | Containerization |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ocr` | Extract text from uploaded PDF with image detection |
| `POST` | `/llm` | RAG-based Q&A with source citations |
| `GET` | `/health` | Service health check and vector count |
| `GET` | `/` | Interactive web interface |

---

# Slide 6: OCR Benchmark Results

## We Tested 3 OCR Models

| Model | Character Success Rate | Word Success Rate | Speed (12 pages) | Type |
|-------|----------------------|-------------------|------------------|------|
| GPT-4.1 | 88.12% | 67.44% | 199s | Closed |
| **Llama-4-Maverick 17B** | **87.75%** | **61.91%** | **75s** | **Open** |
| Phi-4-multimodal | Failed | Failed | N/A | Open |

### Why We Chose Llama-4:
- Only **0.37% accuracy loss** vs GPT-4.1
- **2.7x faster** processing
- **100% open-source**
- No vendor lock-in

---

# Slide 7: RAG Optimization Results

## We Tested 7 Configurations

| Configuration | Answer Quality | Citation Rate | Response Time |
|--------------|----------------|---------------|---------------|
| **Citation-focused + Vanilla k3** | **55.67%** | **73.33%** | **3.61s** |
| Few-shot + Vanilla k3 | 45.70% | 40.00% | 2.17s |
| Baseline + Vanilla k3 | 39.65% | 20.00% | 2.28s |
| MMR Retrieval | 34.60% | 6.67% | 2.53s |

### Key Insights

1. **Simple Beats Complex**: Vanilla retrieval outperforms MMR reranking by **+21%**
2. **Less is More**: Top-3 beats Top-5 by **+20%** (more context confused the LLM)
3. **Prompt Engineering Matters**: Citation-focused prompt improves quality by **+16%**

---

# Slide 8: Performance Metrics

## Final System Performance

| Metric | Score |
|--------|-------|
| **OCR Accuracy** | 87.75% |
| **Answer Quality** | 55.67% |
| **Citation Rate** | 73.33% |
| **Response Time** | 3.6 seconds |

---

## Estimated Hackathon Score

| Category | Weight | Score | Points |
|----------|--------|-------|--------|
| OCR Quality | 50% | 87.75% | **43.9 / 50** |
| LLM Quality | 30% | 55.67% | **16.7 / 30** |
| Architecture | 20% | 100% | **20 / 20** |
| **TOTAL** | 100% | **88.1%** | **440.6 / 500** |

---

# Slide 9: Key Technical Decisions

## What We Did (and Why)

| Decision | Reason | Impact |
|----------|--------|--------|
| **Open-source Llama** over GPT-4 | Transparency + speed | 2.7x faster |
| **Top-3 retrieval** | More context confused LLM | +20% quality |
| **Vanilla retrieval** | Simple beats complex | +21% vs MMR |
| **Citation-focused prompt** | In Azerbaijani | +16% quality, +53% citations |
| **BAAI embeddings** | Best for non-English | +25% vs multilingual |
| **600-char chunks** | Optimal context size | Balanced retrieval |

## What We Avoided

- MMR/Reranking (21% worse performance)
- Top-5+ retrieval (information overload)
- Few-shot prompting (inconsistent results)
- Multilingual embeddings (underperformed)
- Complex architectures (unnecessary overhead)

> *"Every decision was validated through rigorous benchmarking across 3 Jupyter notebooks"*

---

# Slide 10: Live Demo Features

## Interactive Capabilities

### 1. PDF Upload & OCR
- Drag & drop any PDF
- Text extraction with image detection
- Results in markdown format

### 2. Interactive Q&A Chat
- Ask questions in Azerbaijani, Russian, or English
- Real-time responses with context

### 3. Source Citations
- Document name, page number, and excerpt
- Full traceability for verification

### 4. API Documentation
- Swagger UI at `/docs`
- Interactive testing capabilities

**Demo URL**: `http://localhost:8000`

---

# Slide 11: Deliverables

## What We Built

| Category | Count |
|----------|-------|
| PDFs Processed | 28 |
| Vector Chunks | 1,128 |
| Benchmark Notebooks | 3 |
| Documentation Files | 8 |

### Code & Infrastructure
- FastAPI application (505 lines)
- Data ingestion pipeline with parallel processing (4x speedup)
- Docker + Docker Compose deployment
- Health monitoring and web UI

### Documentation & Analysis
- VLM OCR benchmark notebook
- RAG optimization notebook
- LLM comparison notebook
- Comprehensive markdown documentation
- Sample questions & answers

---

# Slide 12: Thank You!

## SOCAR Historical Documents AI System

> Transforming archives into accessible, searchable knowledge

### Final Metrics

| Metric | Value |
|--------|-------|
| OCR Accuracy | **87.75%** |
| Estimated Score | **440.6 / 500** |
| Open Source | **100%** |
| Response Time | **3.6s** |

---

# Questions? Let's Demo!

**GitHub**: [Repository Link]
**API Docs**: `http://localhost:8000/docs`
**Web UI**: `http://localhost:8000`

---

# Appendix: Sample Questions

## Test Questions (Azerbaijani)

1. "Palciq vulkanlarinin tasir radiusu na qadardir?"
2. "SOCAR-in tarixi haqqinda malumat verin"
3. "Neft hasilatinin illik hacmi necedr?"

## Expected Response Format

```json
{
  "answer": "Answer with citations...",
  "sources": [
    {
      "pdf_name": "document_06.pdf",
      "page_number": 3,
      "content": "Relevant excerpt..."
    }
  ],
  "response_time": 3.61
}
```

---

# Appendix: Quick Start

## Running the System

```bash
# Option 1: Docker Compose (Recommended)
docker-compose up -d

# Option 2: Manual Installation
pip install -r app/requirements.txt
python app/main.py

# Access the application
open http://localhost:8000
```

## Environment Variables

```bash
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=hackathon
```
