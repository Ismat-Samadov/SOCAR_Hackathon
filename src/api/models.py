"""Pydantic models for API requests and responses"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class OCRPageResponse(BaseModel):
    """Response model for a single page OCR result"""

    page_number: int = Field(..., description="Page index starting from 1")
    MD_text: str = Field(..., description="Markdown-formatted extracted text")


class OCRResponse(BaseModel):
    """Response model for OCR endpoint"""

    pages: List[OCRPageResponse]
    total_pages: int
    filename: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Message content")


class SourceReference(BaseModel):
    """Source reference for LLM response"""

    pdf_name: str = Field(..., description="Name of the PDF")
    page_number: int = Field(..., description="Page number in the PDF")
    content: str = Field(..., description="Relevant extracted text (in Markdown)")


class LLMResponse(BaseModel):
    """Response model for LLM endpoint"""

    sources: List[SourceReference] = Field(..., description="List of source references")
    answer: str = Field(..., description="Generated answer to the user query")


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    detail: Optional[str] = None
