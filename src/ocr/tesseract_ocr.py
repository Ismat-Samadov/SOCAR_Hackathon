"""Tesseract OCR processor for Azerbaijani text"""

from typing import List, Dict
import io
import base64
from loguru import logger
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


class TesseractOCRProcessor:
    """Process PDFs using Tesseract OCR with Azerbaijani language support"""

    def __init__(self):
        """Initialize Tesseract OCR processor"""
        # Configure Tesseract for Azerbaijani + Turkish + Russian + English
        self.languages = "aze+tur+rus+eng"  # Multi-language support
        logger.info(f"Initialized Tesseract OCR with languages: {self.languages}")

    def process_pdf(self, pdf_file: bytes, pdf_name: str = "document.pdf") -> List[Dict[str, any]]:
        """
        Process PDF and extract text + images using Tesseract OCR

        Args:
            pdf_file: PDF file as bytes
            pdf_name: Name of the PDF file (for logging)

        Returns:
            List of dicts with page_number, MD_text, and images (base64)
        """
        try:
            logger.info(f"Processing PDF with Tesseract ({len(pdf_file)} bytes)")

            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
            pages_data = []

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Extract text using Tesseract
                page_text = self._extract_text_from_page(page, page_num + 1)

                # Extract images
                page_images = self._extract_images_from_page(page, page_num + 1)

                pages_data.append({
                    "page_number": page_num + 1,
                    "MD_text": page_text,
                    "images": page_images
                })

            pdf_document.close()
            logger.info(f"Successfully processed {len(pages_data)} pages with Tesseract")
            return pages_data

        except Exception as e:
            logger.error(f"Error processing PDF with Tesseract: {e}")
            raise

    def _extract_text_from_page(self, page, page_num: int) -> str:
        """
        Extract text from PDF page using Tesseract

        Args:
            page: PyMuPDF page object
            page_num: Page number for logging

        Returns:
            Extracted text (preserving Azerbaijani diacritics)
        """
        try:
            # Render page to image at high resolution (300 DPI)
            mat = fitz.Matrix(300/72, 300/72)  # Scale factor for 300 DPI
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Run Tesseract OCR with Azerbaijani language
            # Preserve original encoding (Azerbaijani diacritics: ə, ı, ö, ü, ğ, ş, ç)
            text = pytesseract.image_to_string(
                img,
                lang=self.languages,
                config='--psm 1 --oem 3'  # PSM 1 = Automatic page segmentation with OSD
            )

            logger.info(f"Extracted {len(text)} characters from page {page_num}")
            return text.strip()

        except Exception as e:
            logger.warning(f"Could not extract text from page {page_num}: {e}")
            return ""

    def _extract_images_from_page(self, page, page_num: int) -> List[str]:
        """
        Extract images from PDF page

        Args:
            page: PyMuPDF page object
            page_num: Page number for logging

        Returns:
            List of base64 encoded images
        """
        images = []

        try:
            # Get images from page
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]

                # Convert to base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                images.append(image_base64)

            if images:
                logger.info(f"Extracted {len(images)} images from page {page_num}")

        except Exception as e:
            logger.warning(f"Could not extract images from page {page_num}: {e}")

        return images


# Singleton instance
_tesseract_ocr_processor = None


def get_tesseract_ocr_processor() -> TesseractOCRProcessor:
    """Get or create Tesseract OCR processor instance"""
    global _tesseract_ocr_processor
    if _tesseract_ocr_processor is None:
        _tesseract_ocr_processor = TesseractOCRProcessor()
    return _tesseract_ocr_processor
