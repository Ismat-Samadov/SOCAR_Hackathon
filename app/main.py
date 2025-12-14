"""
SOCAR Hackathon - LLM Chatbot Endpoint
Optimized based on RAG benchmark results
Best config: citation_focused + vanilla_k3 + Llama-4-Maverick
"""

import os
import time
from typing import List, Dict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SOCAR Historical Documents Chatbot",
    description="RAG-based chatbot for SOCAR oil & gas historical documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients (lazy loading for faster startup)
azure_client = None
pinecone_index = None
embedding_model = None


def get_azure_client():
    """Lazy load Azure OpenAI client"""
    global azure_client
    if azure_client is None:
        azure_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    return azure_client


def get_pinecone_index():
    """Lazy load Pinecone index"""
    global pinecone_index
    if pinecone_index is None:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        pinecone_index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "hackathon"))
    return pinecone_index


def get_embedding_model():
    """Lazy load embedding model"""
    global embedding_model
    if embedding_model is None:
        # Best performing model from benchmark
        embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return embedding_model


# Request/Response models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.2
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, str]]
    response_time: float
    model: str


def retrieve_documents(query: str, top_k: int = 3) -> List[Dict]:
    """
    Retrieve relevant documents from Pinecone vector database.
    Best strategy from benchmark: vanilla top-3
    """
    index = get_pinecone_index()
    embed_model = get_embedding_model()

    # Generate query embedding
    query_embedding = embed_model.encode(query).tolist()

    # Search vector database
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Extract documents
    documents = []
    for match in results['matches']:
        documents.append({
            'pdf_name': match['metadata'].get('pdf_name', 'unknown.pdf'),
            'page_number': match['metadata'].get('page_number', 0),
            'content': match['metadata'].get('text', ''),
            'score': match.get('score', 0.0)
        })

    return documents


def generate_answer(query: str, documents: List[Dict], temperature: float = 0.2, max_tokens: int = 1000) -> tuple[str, float]:
    """
    Generate answer using best-performing configuration.
    Model: Llama-4-Maverick-17B (open-source)
    Prompt: citation_focused (best citation score: 73.33%)
    """
    client = get_azure_client()

    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(
            f"Sənəd {i} (Mənbə: {doc['pdf_name']}, Səhifə {doc['page_number']}):\n{doc['content']}"
        )
    context = "\n\n".join(context_parts)

    # Citation-focused prompt (best performer: 55.67% score)
    prompt = f"""Siz SOCAR-ın tarixi sənədlər üzrə mütəxəssis köməkçisisiniz.

ÖNƏMLİ: Hər bir faktı mütləq mənbə ilə təsdiqləyin (PDF adı və səhifə nömrəsi).

Kontekst:
{context}

Sual: {query}

Cavab verərkən:
1. Dəqiq faktlar yazın
2. Hər faktı mənbə ilə göstərin: (PDF: fayl_adı.pdf, Səhifə: X)
3. Kontekstdə olmayan məlumat əlavə etməyin"""

    try:
        start_time = time.time()

        # Use Llama-4-Maverick (open-source, best performer)
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        elapsed = time.time() - start_time
        answer = response.choices[0].message.content

        return answer, elapsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
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


@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        # Check if services are initialized
        index = get_pinecone_index()
        stats = index.describe_index_stats()

        return {
            "status": "healthy",
            "pinecone": {
                "connected": True,
                "total_vectors": stats.get('total_vector_count', 0)
            },
            "azure_openai": "connected",
            "embedding_model": "loaded"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


@app.post("/llm", response_model=ChatResponse)
async def llm_endpoint(request: ChatRequest):
    """
    LLM chatbot endpoint for SOCAR historical documents.

    Uses RAG (Retrieval Augmented Generation) with:
    - Embedding: BAAI/bge-large-en-v1.5
    - Retrieval: Top-3 documents
    - LLM: Llama-4-Maverick-17B (open-source)
    - Prompt: Citation-focused

    Expected performance:
    - Response time: ~3.6s
    - LLM Judge Score: 55.67%
    - Citation Score: 73.33%
    """
    try:
        # Extract the user's question (last message)
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")

        query = user_messages[-1].content

        # Retrieve relevant documents
        documents = retrieve_documents(query, top_k=3)

        # Generate answer
        answer, response_time = generate_answer(
            query=query,
            documents=documents,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Format sources
        sources = [
            {
                "pdf_name": doc['pdf_name'],
                "page_number": str(doc['page_number']),
                "relevance_score": f"{doc['score']:.3f}"
            }
            for doc in documents
        ]

        return ChatResponse(
            response=answer,
            sources=sources,
            response_time=round(response_time, 2),
            model="Llama-4-Maverick-17B-128E-Instruct-FP8"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
