# SOCAR Hackathon - LLM API Deployment Guide

## Overview

Production-ready FastAPI service for SOCAR historical documents chatbot.

**Configuration (Based on RAG Optimization Benchmark):**
- **Model**: Llama-4-Maverick-17B-128E-Instruct-FP8 (Open-source)
- **Embedding**: BAAI/bge-large-en-v1.5
- **Retrieval**: Top-3 vanilla
- **Prompt Strategy**: Citation-focused
- **Performance**: 55.67% LLM Judge Score, 73.33% Citation Score, ~3.6s response time

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with API keys (see `.env.example`)

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - PINECONE_API_KEY
# - PINECONE_INDEX_NAME
```

### 2. Build and Run with Docker

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f llm-api

# Check health
curl http://localhost:8000/health
```

### 3. Test the API

```bash
# Simple health check
curl http://localhost:8000/

# Test LLM endpoint
curl -X POST http://localhost:8000/llm \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Palçıq vulkanlarının təsir radiusu nə qədərdir?"}
    ]
  }'
```

## API Endpoints

### GET `/`
Root endpoint with service information.

**Response:**
```json
{
  "status": "healthy",
  "service": "SOCAR LLM Chatbot",
  "version": "1.0.0",
  "model": "Llama-4-Maverick-17B (open-source)",
  "configuration": {
    "embedding": "BAAI/bge-large-en-v1.5",
    "retrieval": "top-3 vanilla",
    "prompt": "citation_focused",
    "benchmark_score": "55.67%"
  }
}
```

### GET `/health`
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "pinecone": {
    "connected": true,
    "total_vectors": 1300
  },
  "azure_openai": "connected",
  "embedding_model": "loaded"
}
```

### POST `/llm`
Main chatbot endpoint.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Your question here"}
  ],
  "temperature": 0.2,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "response": "Answer with citations...",
  "sources": [
    {
      "pdf_name": "document_00.pdf",
      "page_number": "5",
      "relevance_score": "0.892"
    }
  ],
  "response_time": 3.61,
  "model": "Llama-4-Maverick-17B-128E-Instruct-FP8"
}
```

## Development Mode

### Run locally without Docker

```bash
# Install dependencies
cd app
pip install -r requirements.txt

# Run with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access API documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

### Environment Variables

Required in `.env`:
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Pinecone
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=hackathon
```

### Docker Commands

```bash
# Build
docker-compose build --no-cache

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Remove everything
docker-compose down -v
```

### Health Checks

The Docker container includes automatic health checks:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 40 seconds (for model loading)
- **Retries**: 3

### Monitoring

```bash
# Check container status
docker-compose ps

# View resource usage
docker stats socar-llm-api

# Check logs
docker-compose logs --tail=100 llm-api
```

## Performance Optimization

### Lazy Loading
- Azure client, Pinecone index, and embedding model are lazy-loaded
- First request may take longer (~5-10s for model loading)
- Subsequent requests: ~3.6s average

### Caching (Future)
To improve performance, consider:
- Redis for frequently asked questions
- Embedding cache for common queries
- Model quantization for faster inference

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs llm-api

# Verify environment variables
docker-compose config

# Rebuild
docker-compose build --no-cache
```

### API returns 500 errors
- Check Azure OpenAI key and endpoint
- Verify Pinecone connection
- Check model deployment name matches

### Slow responses
- First request loads models (5-10s)
- Subsequent requests should be ~3-4s
- Check network connectivity to Azure/Pinecone

## Architecture Score

**Open-Source Stack (20% bonus):**
- ✅ Llama-4-Maverick-17B (Open-source LLM)
- ✅ BAAI/bge-large-en-v1.5 (Open-source embeddings)
- ✅ FastAPI (Open-source framework)
- ✅ Docker (Open-source deployment)

**Total Architecture Score: Maximum 20% for hackathon!**

## License

Built for SOCAR Hackathon 2025
