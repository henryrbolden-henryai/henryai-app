"""Text processing utilities for document extraction and JSON cleaning"""

from fastapi import HTTPException


def clean_claude_json(text: str) -> str:
    """Aggressively clean Claude's response to extract valid JSON"""
    # Remove code fences
    if text.strip().startswith("```"):
        parts = text.strip().split("```")
        text = parts[1] if len(parts) > 1 else text
    # Remove "json" prefix inside code blocks
    text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()
    # Remove leading non-json content
    first_brace = text.find("{")
    if first_brace != -1:
        text = text[first_brace:]
    # Remove trailing junk after last closing brace
    last_brace = text.rfind("}")
    if last_brace != -1:
        text = text[:last_brace + 1]
    return text


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF file using PyMuPDF (fitz)"""
    try:
        import fitz  # PyMuPDF

        # Open PDF from bytes
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        # Clean the text
        text = text.replace('\x00', '')  # Remove null bytes

        if not text.strip():
            raise ValueError("No text extracted from PDF")

        return text.strip()
    except ImportError:
        # Fallback to PyPDF2 if fitz not available
        try:
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX file using python-docx"""
    try:
        from docx import Document
        from io import BytesIO

        print("📄 Attempting to parse DOCX file...")
        doc = Document(BytesIO(file_bytes))

        # Extract text from paragraphs
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        print(f"📄 Found {len(paragraphs)} paragraphs")

        # Also extract text from tables (resumes often use tables for layout)
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    table_text.append(' | '.join(row_text))
        print(f"📄 Found {len(table_text)} table rows")

        # Combine all text
        all_text = paragraphs + table_text
        text = '\n'.join(all_text)

        # Clean the text
        text = text.replace('\x00', '')  # Remove null bytes

        if not text.strip():
            raise ValueError("No text extracted from DOCX")

        print(f"📄 Successfully extracted {len(text)} characters from DOCX")
        return text.strip()
    except Exception as e:
        print(f"🔥 DOCX EXTRACTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"DOCX extraction failed: {str(e)}")
