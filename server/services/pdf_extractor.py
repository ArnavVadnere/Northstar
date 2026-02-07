"""
PDF Text Extraction Service

Extracts text content from uploaded PDF files using PyMuPDF (fitz).
Returns structured output with full text and per-page breakdown.
"""
import fitz  # PyMuPDF
from typing import BinaryIO, Union
from pathlib import Path
import io


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


def extract_text_from_pdf(
    pdf_source: Union[bytes, BinaryIO, str, Path]
) -> dict:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_source: PDF content as bytes, file-like object, or path to file
    
    Returns:
        Structured output:
        {
            "full_text": "...",           # All text concatenated
            "pages": [
                {"page_num": 1, "text": "..."},
                {"page_num": 2, "text": "..."},
                ...
            ],
            "page_count": 5,
            "metadata": {
                "title": "...",
                "author": "...",
                "subject": "...",
                "creator": "..."
            }
        }
    
    Raises:
        PDFExtractionError: If the PDF cannot be processed
    """
    try:
        # Handle different input types
        if isinstance(pdf_source, (str, Path)):
            doc = fitz.open(str(pdf_source))
        elif isinstance(pdf_source, bytes):
            doc = fitz.open(stream=pdf_source, filetype="pdf")
        else:
            # File-like object - read bytes
            content = pdf_source.read()
            if hasattr(pdf_source, 'seek'):
                pdf_source.seek(0)  # Reset for potential reuse
            doc = fitz.open(stream=content, filetype="pdf")
        
    except fitz.fitz.FileDataError as e:
        raise PDFExtractionError(f"Invalid or corrupted PDF file: {e}")
    except fitz.fitz.FileNotFoundError as e:
        raise PDFExtractionError(f"PDF file not found: {e}")
    except Exception as e:
        raise PDFExtractionError(f"Failed to open PDF: {e}")
    
    try:
        # Check for encryption/password protection
        if doc.is_encrypted:
            # Try to decrypt with empty password (some PDFs are "protected" but not locked)
            if not doc.authenticate(""):
                raise PDFExtractionError("PDF is password-protected and cannot be processed")
        
        # Check for empty PDF
        if doc.page_count == 0:
            raise PDFExtractionError("PDF contains no pages")
        
        # Extract text from each page
        pages = []
        full_text_parts = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text("text")
            
            pages.append({
                "page_num": page_num + 1,  # 1-indexed
                "text": text.strip()
            })
            full_text_parts.append(text)
        
        full_text = "\n\n".join(full_text_parts)
        
        # Extract metadata
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", "")
        }
        
        doc.close()
        
        return {
            "full_text": full_text.strip(),
            "pages": pages,
            "page_count": len(pages),
            "metadata": metadata
        }
        
    except PDFExtractionError:
        doc.close()
        raise
    except Exception as e:
        doc.close()
        raise PDFExtractionError(f"Error extracting text from PDF: {e}")


async def extract_text_from_upload(upload_file) -> dict:
    """
    Extract text from a FastAPI UploadFile.
    
    Args:
        upload_file: FastAPI UploadFile object
    
    Returns:
        Same structured output as extract_text_from_pdf
    
    Raises:
        PDFExtractionError: If the PDF cannot be processed
    """
    content = await upload_file.read()
    await upload_file.seek(0)  # Reset for potential reuse
    
    if not content:
        raise PDFExtractionError("Empty file uploaded")
    
    return extract_text_from_pdf(content)


def get_text_by_page(extracted_data: dict, page_num: int) -> str:
    """
    Get text for a specific page from extracted data.
    
    Args:
        extracted_data: Output from extract_text_from_pdf
        page_num: Page number (1-indexed)
    
    Returns:
        Text content of the specified page, or empty string if not found
    """
    for page in extracted_data.get("pages", []):
        if page["page_num"] == page_num:
            return page["text"]
    return ""


def search_text_in_pages(extracted_data: dict, search_term: str) -> list:
    """
    Search for a term across all pages.
    
    Args:
        extracted_data: Output from extract_text_from_pdf
        search_term: Text to search for (case-insensitive)
    
    Returns:
        List of matches: [{"page_num": 1, "context": "...matching text..."}]
    """
    matches = []
    search_lower = search_term.lower()
    
    for page in extracted_data.get("pages", []):
        text = page["text"]
        if search_lower in text.lower():
            # Find the matching context (50 chars before and after)
            idx = text.lower().find(search_lower)
            start = max(0, idx - 50)
            end = min(len(text), idx + len(search_term) + 50)
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            
            matches.append({
                "page_num": page["page_num"],
                "context": context.strip()
            })
    
    return matches
