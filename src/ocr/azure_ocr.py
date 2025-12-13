"""Azure Document Intelligence OCR processor"""

from typing import List, Dict
from pathlib import Path
import io
from loguru import logger

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from src.config import settings


class AzureOCRProcessor:
    """Process PDFs using Azure Document Intelligence"""

    def __init__(self):
        """Initialize Azure Document Intelligence client"""
        # Use Azure OpenAI endpoint as Document Intelligence endpoint
        # In production, these might be different
        endpoint = settings.azure_openai_endpoint.rstrip("/")
        api_key = settings.azure_openai_api_key

        self.client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(api_key)
        )
        logger.info("Initialized Azure Document Analysis client")

    def process_pdf(self, pdf_file: bytes) -> List[Dict[str, any]]:
        """
        Process PDF and extract text using Azure Document Intelligence

        Args:
            pdf_file: PDF file as bytes

        Returns:
            List of dicts with page_number and MD_text
        """
        try:
            logger.info(f"Processing PDF ({len(pdf_file)} bytes)")

            # Analyze document using Azure Form Recognizer
            poller = self.client.begin_analyze_document(
                "prebuilt-read", document=io.BytesIO(pdf_file)
            )
            result = poller.result()

            # Extract text page by page
            pages_data = []
            for page_num, page in enumerate(result.pages, start=1):
                # Collect all lines from this page
                lines = []
                if hasattr(page, 'lines') and page.lines:
                    for line in page.lines:
                        lines.append(line.content)

                page_text = "\n".join(lines) if lines else ""

                pages_data.append({
                    "page_number": page_num,
                    "MD_text": page_text
                })

            logger.info(f"Successfully processed {len(pages_data)} pages")
            return pages_data

        except Exception as e:
            logger.error(f"Error processing PDF with Azure: {e}")
            raise


# Singleton instance
_azure_ocr_processor = None


def get_azure_ocr_processor() -> AzureOCRProcessor:
    """Get or create Azure OCR processor instance"""
    global _azure_ocr_processor
    if _azure_ocr_processor is None:
        _azure_ocr_processor = AzureOCRProcessor()
    return _azure_ocr_processor
