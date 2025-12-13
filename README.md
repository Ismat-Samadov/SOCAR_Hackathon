# SOCAR Historical Document Processing Challenge

AI-powered system for processing historical handwritten and printed documents from SOCAR's oil and gas research archives.

## Overview

This solution transforms historical documents into an interactive, searchable knowledge base using:
- **OCR Processing** - Extract text from handwritten and printed PDFs (multi-language support)
- **Vector Database** - Store and retrieve document information efficiently
- **RAG Chatbot** - Answer questions using historical document knowledge

## Quick Start

### Option 1: Docker Deployment (Recommended)

#### Using Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### Using Docker Directly

```bash
# Build the image
docker build -t socar-document-processing .

# Run the container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  --name socar-api \
  socar-document-processing

# View logs
docker logs -f socar-api

# Stop the container
docker stop socar-api
```

The API will be available at `http://localhost:8000`

### Option 2: Local Python Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure Environment

Ensure `.env` file exists with your credentials:

Required variables:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `LLM_MODEL` - Model name (default: Llama-4-Maverick-17B-128E-Instruct-FP8)

#### 3. Run the API Server

```bash
python run.py
```

The API will be available at `http://localhost:8000`

#### 4. Test the System

```bash
python test_complete_system.py
```

## API Endpoints

### POST /ocr

Extract text from PDF documents.

**Request:**
```bash
curl -X POST http://localhost:8000/ocr \
  -F "file=@document.pdf"
```

**Response:**
```json
[
  {
    "page_number": 1,
    "MD_text": "## Section Title\nExtracted text..."
  }
]
```

### POST /llm

Query documents using natural language.

**Request:**
```bash
curl -X POST http://localhost:8000/llm \
  -H "Content-Type: application/json" \
  -d '[{"role": "user", "content": "What is this document about?"}]'
```

**Response:**
```json
{
  "sources": [
    {
      "pdf_name": "document.pdf",
      "page_number": 1,
      "content": "Relevant text snippet..."
    }
  ],
  "answer": "This document discusses..."
}
```

## Project Structure

```
.
├── src/
│   ├── api/           # FastAPI endpoints
│   ├── ocr/           # OCR processing modules
│   ├── llm/           # LLM and RAG pipeline
│   └── utils/         # Utility functions
├── data/
│   ├── pdfs/          # Input PDF documents
│   ├── processed/     # Processed documents
│   └── vector_db/     # Vector database storage
├── tests/             # Test files
├── run.py             # Application entry point
└── requirements.txt   # Python dependencies
```

## Technologies

- **OCR**: Azure Document Intelligence (multi-language support)
- **Vector DB**: ChromaDB (local, open-source)
- **LLM**: Llama-4-Maverick-17B (open-source, deployable)
- **API**: FastAPI (async, high-performance)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Deployment**: Docker, Docker Compose

## Deployment

### Docker Features

- **Multi-stage build** - Optimized image size
- **Health checks** - Automatic container monitoring
- **Volume mounts** - Persistent data storage
- **Environment variables** - Easy configuration
- **Auto-restart** - Production-ready resilience

### Production Deployment

```bash
# Build production image
docker build -t socar-api:production .

# Deploy with nginx reverse proxy
docker network create socar-network
docker run -d --name socar-api --network socar-network socar-api:production
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## License

MIT License - SOCAR Hackathon 2024
