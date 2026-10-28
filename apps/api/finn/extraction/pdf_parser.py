import io
import hashlib
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from pypdf import PdfReader

class ParsedPage(BaseModel):
    pdf_page_1based: int
    printed_label: Optional[str] = None
    text: str
    char_count: int
    ocr_flag: bool = False

class PDFParseResult(BaseModel):
    status: str = Field(..., description="verified | scanned_needs_ocr | corrupt_or_invalid")
    sha256: str
    file_size_bytes: int
    page_count: int
    pages: List[ParsedPage] = Field(default_factory=list)
    error_message: Optional[str] = None

def parse_pdf(file_input: Union[bytes, str]) -> PDFParseResult:
    """Parses PDF content into 1-based indexed pages with text extraction,

    verifying file integrity, SHA-256 checksum, and detecting scanned documents.
    """
    if isinstance(file_input, str):
        with open(file_input, "rb") as f:
            content = f.read()
    else:
        content = file_input

    size = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    # Validate PDF magic header
    if not content.startswith(b"%PDF-"):
        return PDFParseResult(
            status="corrupt_or_invalid",
            sha256=sha256,
            file_size_bytes=size,
            page_count=0,
            error_message="Invalid file format: Missing %PDF- magic header (possible HTML error page)"
        )

    try:
        reader = PdfReader(io.BytesIO(content))
        page_count = len(reader.pages)
        if page_count == 0:
            return PDFParseResult(
                status="corrupt_or_invalid",
                sha256=sha256,
                file_size_bytes=size,
                page_count=0,
                error_message="PDF contains 0 pages"
            )

        parsed_pages: List[ParsedPage] = []
        total_text_length = 0

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""

            cleaned_text = page_text.strip()
            char_count = len(cleaned_text)
            total_text_length += char_count

            parsed_pages.append(ParsedPage(
                pdf_page_1based=page_num,
                printed_label=str(page_num),
                text=cleaned_text,
                char_count=char_count,
                ocr_flag=False
            ))

        # Check if document appears to be scanned images without text layer
        avg_chars_per_page = total_text_length / page_count
        status = "verified"
        error_msg = None

        if avg_chars_per_page < 40 and page_count > 1:
            status = "scanned_needs_ocr"
            error_msg = f"Document has low text density ({round(avg_chars_per_page, 1)} chars/page); likely scanned image"

        return PDFParseResult(
            status=status,
            sha256=sha256,
            file_size_bytes=size,
            page_count=page_count,
            pages=parsed_pages,
            error_message=error_msg
        )

    except Exception as e:
        return PDFParseResult(
            status="corrupt_or_invalid",
            sha256=sha256,
            file_size_bytes=size,
            page_count=0,
            error_message=f"PDF parsing exception: {str(e)}"
        )
