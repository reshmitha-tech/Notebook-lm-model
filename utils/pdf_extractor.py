"""
pdf_extractor.py - Extracts text from uploaded PDF files using PyPDF2.
"""
import PyPDF2
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        file_path: Absolute path to the PDF file.
    
    Returns:
        Extracted text as a string. Returns empty string on failure.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    text_parts = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to extract PDF text: {e}")

    return "\n\n".join(text_parts)
