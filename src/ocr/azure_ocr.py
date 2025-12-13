"""Azure Document Intelligence OCR processor"""

from typing import List, Dict
from pathlib import Path
import io
from loguru import logger

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import fitz  # PyMuPDF for image detection

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

    def process_pdf(self, pdf_file: bytes, pdf_name: str = "document.pdf") -> List[Dict[str, any]]:
        """
        Process PDF and extract text + images using Azure Document Intelligence

        Args:
            pdf_file: PDF file as bytes
            pdf_name: Name of the PDF file (for logging)

        Returns:
            List of dicts with page_number and MD_text (with inline images)
        """
        try:
            logger.info(f"Processing PDF ({len(pdf_file)} bytes)")

            # Analyze document using Azure Form Recognizer
            poller = self.client.begin_analyze_document(
                "prebuilt-read", document=io.BytesIO(pdf_file)
            )
            result = poller.result()

            # Detect images using PyMuPDF (don't save, just mention)
            doc_name = Path(pdf_name).stem  # Get filename without extension
            images_by_page = self._detect_images(pdf_file, doc_name)

            # Extract text page by page
            pages_data = []
            for page_num, page in enumerate(result.pages, start=1):
                # Collect all lines from this page (PRESERVE CYRILLIC)
                lines = []
                if hasattr(page, 'lines') and page.lines:
                    for line in page.lines:
                        # Azure OCR preserves original encoding (Cyrillic stays Cyrillic)
                        lines.append(line.content)

                page_text = "\n".join(lines) if lines else ""

                # Get image references for this page
                page_images = images_by_page.get(page_num - 1, [])  # 0-indexed

                # Only add image markdown if images exist
                if page_images:
                    for img_ref in page_images:
                        # Create markdown image mention (no actual file)
                        md_image = f'\n\n![Image]({img_ref})\n\n'
                        page_text += md_image

                    logger.info(f"Added {len(page_images)} image references for page {page_num}")

                pages_data.append({
                    "page_number": page_num,
                    "MD_text": page_text
                })

            logger.info(f"Successfully processed {len(pages_data)} pages")
            return pages_data

        except Exception as e:
            logger.error(f"Error processing PDF with Azure: {e}")
            raise

    def _detect_images(self, pdf_file: bytes, doc_name: str) -> Dict[int, List[str]]:
        """
        Detect images in PDF (don't save, just mention their presence)

        Args:
            pdf_file: PDF file as bytes
            doc_name: Document name (without extension)

        Returns:
            Dict mapping page_number (0-indexed) to list of image references
        """
        images_by_page = {}

        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_refs = []

                # Get images from page
                image_list = page.get_images()

                # Only process if images exist on this page
                if image_list:
                    for img_index, img in enumerate(image_list):
                        # Create simple reference: document_page_X_image_Y
                        img_ref = f"{doc_name}_page_{page_num + 1}_image_{img_index + 1}"
                        image_refs.append(img_ref)

                    if image_refs:
                        images_by_page[page_num] = image_refs
                        logger.info(f"Detected {len(image_refs)} images on page {page_num + 1}")

            pdf_document.close()

        except Exception as e:
            logger.warning(f"Could not detect images: {e}")

        return images_by_page


# Singleton instance
_azure_ocr_processor = None


def get_azure_ocr_processor() -> AzureOCRProcessor:
    """Get or create Azure OCR processor instance"""
    global _azure_ocr_processor
    if _azure_ocr_processor is None:
        _azure_ocr_processor = AzureOCRProcessor()
    return _azure_ocr_processor
