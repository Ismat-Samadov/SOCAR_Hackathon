"""Main OCR processor that handles different backends"""

from typing import List, Dict
from pathlib import Path
from loguru import logger

from src.config import settings


class OCRProcessor:
    """Main OCR processor that can switch between different backends"""

    def __init__(self, backend: str = None):
        """
        Initialize OCR processor

        Args:
            backend: OCR backend to use (azure, paddle, easy, tesseract)
                    If None, uses settings.ocr_backend
        """
        self.backend = backend or settings.ocr_backend
        logger.info(f"Initializing OCR processor with backend: {self.backend}")

        # Initialize the appropriate processor
        if self.backend == "azure":
            from src.ocr.azure_ocr import get_azure_ocr_processor
            self.processor = get_azure_ocr_processor()
        else:
            raise ValueError(f"Unsupported OCR backend: {self.backend}")

    def process_pdf(self, pdf_file: bytes, filename: str = None) -> List[Dict[str, any]]:
        """
        Process PDF file and extract text

        Args:
            pdf_file: PDF file as bytes
            filename: Optional filename for logging

        Returns:
            List of dicts with page_number and MD_text
        """
        logger.info(f"Processing PDF: {filename or 'unnamed'} ({len(pdf_file)} bytes)")

        try:
            result = self.processor.process_pdf(pdf_file)
            logger.info(f"Successfully processed {len(result)} pages")
            return result
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise


# Singleton instance
_ocr_processor = None


def get_ocr_processor() -> OCRProcessor:
    """Get or create OCR processor instance"""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor()
    return _ocr_processor
