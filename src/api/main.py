"""FastAPI application with OCR and LLM endpoints"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, Response
from typing import List
from loguru import logger
import sys

from src.api.models import (
    OCRPageResponse,
    ChatMessage,
    LLMResponse,
    ErrorResponse,
)
from src.ocr.processor import get_ocr_processor
from src.config import settings

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create FastAPI app
app = FastAPI(
    title="SOCAR Historical Document Processing API",
    description="OCR and LLM endpoints for processing historical documents",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SOCAR Document Processing API",
        "endpoints": ["/ocr", "/llm"],
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return favicon for browser tab"""
    # Simple SVG favicon representing oil/gas industry
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="#0066cc"/>
        <path d="M30 60 L50 30 L70 60 Z" fill="#ffffff"/>
        <rect x="45" y="55" width="10" height="30" fill="#ffffff"/>
    </svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@app.post(
    "/ocr",
    response_model=List[OCRPageResponse],
    responses={
        200: {"description": "Successfully processed PDF"},
        400: {"model": ErrorResponse, "description": "Invalid PDF file"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
)
async def process_ocr(file: UploadFile = File(...)):
    """
    OCR Endpoint - Extract text from PDF documents

    Accepts a PDF file upload and returns the extracted Markdown text for each page.

    Args:
        file: PDF file in multipart/form-data format

    Returns:
        List of dictionaries with page_number and MD_text for each page
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are accepted.",
            )

        # Read file content
        logger.info(f"Receiving PDF file: {file.filename}")
        pdf_content = await file.read()

        if len(pdf_content) == 0:
            raise HTTPException(status_code=400, detail="Empty PDF file")

        # Process PDF with OCR
        ocr_processor = get_ocr_processor()
        result = ocr_processor.process_pdf(pdf_content, file.filename)

        # Convert to response format
        response = [
            OCRPageResponse(page_number=page["page_number"], MD_text=page["MD_text"])
            for page in result
        ]

        logger.info(f"Successfully processed {len(response)} pages from {file.filename}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR request: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process PDF: {str(e)}"
        )


@app.post(
    "/llm",
    response_model=LLMResponse,
    responses={
        200: {"description": "Successfully generated response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
)
async def process_llm(messages: List[ChatMessage]):
    """
    LLM Endpoint - Generate answers from document knowledge base

    Receives chat history and produces an LLM-generated answer along with source references.

    Args:
        messages: List of chat messages with role and content

    Returns:
        Dictionary with sources and answer
    """
    try:
        # Validate input
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        logger.info(f"Received {len(messages)} messages for LLM processing")

        # Get the last user message as the query
        last_message = messages[-1]
        if last_message.role != "user":
            raise HTTPException(
                status_code=400,
                detail="Last message must be from user",
            )

        query = last_message.content

        # Prepare chat history (all messages except the last one)
        chat_history = None
        if len(messages) > 1:
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages[:-1]
            ]

        # Process query using RAG pipeline
        from src.llm.rag_pipeline import get_rag_pipeline

        rag = get_rag_pipeline()
        result = rag.query(query, chat_history=chat_history)

        logger.info(f"Generated answer with {len(result['sources'])} sources")

        return LLMResponse(
            sources=result["sources"],
            answer=result["answer"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing LLM request: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
