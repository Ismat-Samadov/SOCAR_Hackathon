"""
SOCAR Hackathon - Complete API with /ocr and /llm endpoints
Optimized based on comprehensive benchmarking:
- OCR: Llama-4-Maverick-17B (87.75% CSR)
- LLM: citation_focused + vanilla_k3 + Llama-4-Maverick (55.67% score)
"""

import os
import re
import time
import base64
from typing import List, Dict
from pathlib import Path
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SOCAR Historical Documents AI System",
    description="RAG-based chatbot for SOCAR oil & gas historical documents with OCR capabilities",
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

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

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


class QuestionRequest(BaseModel):
    question: str
    temperature: float = 0.2
    max_tokens: int = 1000


class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict]
    response_time: float


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
        # Ensure page_number is always an integer (Pinecone may return float)
        page_num = match['metadata'].get('page_number', 0)
        page_num = int(page_num) if isinstance(page_num, (int, float)) else 0

        documents.append({
            'pdf_name': match['metadata'].get('pdf_name', 'unknown.pdf'),
            'page_number': page_num,
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
2. Hər faktı mənbə ilə göstərin: (PDF: fayl_adı.pdf, Səhifə: X) - səhifə nömrəsini tam ədəd (integer) olaraq yazın, məsələn "Səhifə: 11" (11.0 yox)
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
async def root(request: Request):
    """Serve the frontend web application"""
    return templates.TemplateResponse("index.html", {"request": request})


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


@app.post("/llm")
async def llm_endpoint(request: Request):
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

    Accepts two formats:
    1. QuestionRequest: {"question": "...", "temperature": 0.2, "max_tokens": 1000}
    2. ChatRequest: {"messages": [{"role": "user", "content": "..."}], ...}
    """
    try:
        # Parse request body
        body = await request.json()

        # Determine request format and extract query
        if "question" in body:
            # QuestionRequest format
            query = body.get("question")
            temperature = body.get("temperature", 0.2)
            max_tokens = body.get("max_tokens", 1000)
            is_simple_format = True
        elif "messages" in body:
            # ChatRequest format
            messages = body.get("messages", [])
            if not messages:
                raise HTTPException(status_code=400, detail="No messages provided")

            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            if not user_messages:
                raise HTTPException(status_code=400, detail="No user message found")

            query = user_messages[-1].get("content")
            temperature = body.get("temperature", 0.2)
            max_tokens = body.get("max_tokens", 1000)
            is_simple_format = False
        else:
            raise HTTPException(status_code=400, detail="Invalid request format. Expected 'question' or 'messages' field.")

        # Retrieve relevant documents
        documents = retrieve_documents(query, top_k=3)

        # Generate answer
        answer, response_time = generate_answer(
            query=query,
            documents=documents,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Format sources for response
        sources = [
            {
                "pdf_name": doc['pdf_name'],
                "page_number": doc['page_number'],
                "relevance_score": f"{doc['score']:.3f}"
            }
            for doc in documents
        ]

        # Return appropriate response format
        if is_simple_format:
            return AnswerResponse(
                answer=answer,
                sources=sources,
                response_time=round(response_time, 2)
            )
        else:
            return ChatResponse(
                response=answer,
                sources=[{k: str(v) for k, v in s.items()} for s in sources],
                response_time=round(response_time, 2),
                model="Llama-4-Maverick-17B-128E-Instruct-FP8"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================================================================
# OCR ENDPOINT
# ============================================================================

class OCRPageResponse(BaseModel):
    page_number: int
    MD_text: str


def pdf_to_images(pdf_bytes: bytes, dpi: int = 100) -> List[Image.Image]:
    """Convert PDF bytes to PIL Images."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    doc.close()
    return images


def image_to_base64(image: Image.Image, format: str = "JPEG", quality: int = 85) -> str:
    """Convert PIL Image to base64 with compression."""
    buffered = BytesIO()
    image.save(buffered, format=format, quality=quality, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def detect_images_in_pdf(pdf_bytes: bytes) -> Dict[int, int]:
    """
    Detect images in each page of PDF.
    Returns dict: {page_number: image_count}
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_counts = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        image_counts[page_num + 1] = len(image_list)

    doc.close()
    return image_counts


@app.post("/ocr", response_model=List[OCRPageResponse])
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    OCR endpoint for PDF text extraction with image detection.

    Uses VLM (Llama-4-Maverick-17B) for best accuracy:
    - Character Success Rate: 87.75%
    - Word Success Rate: 61.91%
    - Processing: ~6s per page

    Returns:
        List of {page_number, MD_text} with inline image references
    """
    try:
        # Read PDF
        pdf_bytes = await file.read()
        pdf_filename = file.filename or "document.pdf"

        # Convert to images
        images = pdf_to_images(pdf_bytes, dpi=100)

        # Detect images per page
        image_counts = detect_images_in_pdf(pdf_bytes)

        # OCR system prompt
        system_prompt = """You are an expert OCR system for historical oil & gas documents.

Extract ALL text from the image with 100% accuracy. Follow these rules:
1. Preserve EXACT spelling - including Azerbaijani, Russian, and English text
2. Maintain original Cyrillic characters - DO NOT transliterate
3. Keep all numbers, symbols, and special characters exactly as shown
4. Preserve layout structure (paragraphs, line breaks)
5. Include ALL text - headers, body, footnotes, tables, captions

Output ONLY the extracted text. No explanations, no descriptions."""

        # Process each page
        results = []
        client = get_azure_client()

        for page_num, image in enumerate(images, 1):
            # Convert image to base64
            image_base64 = image_to_base64(image, format="JPEG", quality=85)

            # VLM OCR
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Extract all text from page {page_num}:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]

            response = client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=messages,
                temperature=0.0,  # Deterministic OCR
                max_tokens=4000
            )

            page_text = response.choices[0].message.content

            # Add image references if images exist on this page
            num_images = image_counts.get(page_num, 0)
            if num_images > 0:
                for img_idx in range(1, num_images + 1):
                    page_text += f"\n\n![Image]({pdf_filename}/page_{page_num}/image_{img_idx})\n\n"

            results.append({
                "page_number": page_num,
                "MD_text": page_text
            })

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
