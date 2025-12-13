"""Azure Document Intelligence OCR processor"""

from typing import List, Dict
from pathlib import Path
import io
import base64
from loguru import logger

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import fitz  # PyMuPDF for image extraction

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

            # Extract images with metadata using PyMuPDF
            images_by_page = self._extract_images_from_pdf(pdf_file)

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

                # Get images for this page and embed them inline
                page_images = images_by_page.get(page_num - 1, [])  # 0-indexed

                # Embed images inline in markdown text
                if page_images:
                    for img_idx, img_data in enumerate(page_images, start=1):
                        # Determine image format from base64 header
                        img_format = img_data.get("format", "png")
                        img_base64 = img_data.get("base64", "")

                        # Create markdown image with data URI
                        md_image = f'\n\n![Image {img_idx}](data:image/{img_format};base64,{img_base64})\n\n'
                        page_text += md_image

                    logger.info(f"Embedded {len(page_images)} images inline for page {page_num}")

                pages_data.append({
                    "page_number": page_num,
                    "MD_text": page_text
                })

            logger.info(f"Successfully processed {len(pages_data)} pages")
            return pages_data

        except Exception as e:
            logger.error(f"Error processing PDF with Azure: {e}")
            raise

    def _extract_images_from_pdf(self, pdf_file: bytes) -> Dict[int, List[Dict[str, str]]]:
        """
        Extract images from PDF using PyMuPDF

        Args:
            pdf_file: PDF file as bytes

        Returns:
            Dict mapping page_number (0-indexed) to list of image dicts with format and base64
        """
        images_by_page = {}

        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                images = []

                # Get images from page
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Determine image format (png, jpeg, etc.)
                    img_ext = base_image.get("ext", "png")
                    # Normalize format names (jpeg vs jpg)
                    img_format = "jpeg" if img_ext in ["jpg", "jpeg"] else img_ext

                    # Convert to base64
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

                    images.append({
                        "format": img_format,
                        "base64": image_base64
                    })

                if images:
                    images_by_page[page_num] = images
                    logger.info(f"Extracted {len(images)} images from page {page_num + 1}")

            pdf_document.close()

        except Exception as e:
            logger.warning(f"Could not extract images: {e}")

        return images_by_page


# Singleton instance
_azure_ocr_processor = None


def get_azure_ocr_processor() -> AzureOCRProcessor:
    """Get or create Azure OCR processor instance"""
    global _azure_ocr_processor
    if _azure_ocr_processor is None:
        _azure_ocr_processor = AzureOCRProcessor()
    return _azure_ocr_processor
