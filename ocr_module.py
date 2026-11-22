"""
OCR Module for extracting text from scanned/image-based PDFs
"""
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import io
import tempfile
import os


class OCRProcessor:
    """Handles OCR processing for scanned PDFs"""
    
    def __init__(self):
        self.tesseract_cmd = self._find_tesseract()
    
    def _find_tesseract(self):
        """Find Tesseract executable path"""
        # Common paths for different OS
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def configure_tesseract(self, custom_path=None):
        """Configure Tesseract path"""
        if custom_path:
            pytesseract.pytesseract.tesseract_cmd = custom_path
        elif self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
    
    def extract_text_from_image(self, image):
        """Extract text from a single image"""
        try:
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_text_from_pdf_images(self, pdf_file, dpi=300):
        """
        Extract text from PDF by converting pages to images first
        This handles scanned/image-based PDFs
        """
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_file.read())
                tmp_pdf_path = tmp_pdf.name
            
            # Convert PDF to images
            images = convert_from_path(tmp_pdf_path, dpi=dpi)
            
            # Extract text from each image
            full_text = ""
            for i, image in enumerate(images):
                text = self.extract_text_from_image(image)
                full_text += text + "\n"
            
            # Clean up temporary file
            os.unlink(tmp_pdf_path)
            
            return full_text
        
        except Exception as e:
            raise Exception(f"PDF to image conversion failed: {str(e)}")
    
    def is_scanned_pdf(self, pdf_file, sample_pages=2):
        """
        Check if PDF is likely scanned/image-based
        by attempting text extraction first
        """
        from PyPDF2 import PdfReader
        
        try:
            pdf_reader = PdfReader(pdf_file)
            # Check first few pages
            for i in range(min(sample_pages, len(pdf_reader.pages))):
                text = pdf_reader.pages[i].extract_text()
                if text and len(text.strip()) > 50:
                    return False  # Has extractable text
            return True  # Likely scanned
        except:
            return True


def get_ocr_processor():
    """Factory function to get OCR processor"""
    processor = OCRProcessor()
    processor.configure_tesseract()
    return processor
