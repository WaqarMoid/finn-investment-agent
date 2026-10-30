import re
import uuid
import sqlite3
from typing import List, Dict, Any, Optional
from finn.extraction.pdf_parser import ParsedPage

class DocumentChunkModel:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        company_id: str,
        page_start: int,
        page_end: int,
        section: Optional[str],
        text_content: str,
        token_estimate: int
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.company_id = company_id
        self.page_start = page_start
        self.page_end = page_end
        self.section = section
        self.text_content = text_content
        self.token_estimate = token_estimate

def chunk_document_pages(
    document_id: str,
    company_id: str,
    pages: List[ParsedPage],
    chunk_size_chars: int = 700,
    overlap_chars: int = 100
) -> List[DocumentChunkModel]:
    """Splits document pages into cohesive chunks preserving page boundaries and sections."""
    chunks: List[DocumentChunkModel] = []
    
    current_section = "General Overview"
    current_text = ""
    current_start_page = 1

    for page in pages:
        page_text = page.text
        if not page_text:
            continue

        # Simple section header heuristic (e.g. all-caps lines or lines starting with 'Section')
        lines = page_text.splitlines()
        for line in lines[:3]:
            trimmed = line.strip()
            if len(trimmed) > 3 and len(trimmed) < 60 and (trimmed.isupper() or "Quarterly" in trimmed or "Report" in trimmed):
                current_section = trimmed
                break

        # If accumulator is empty, set start page
        if not current_text:
            current_start_page = page.pdf_page_1based

        current_text += f"\n[Page {page.pdf_page_1based}]\n" + page_text

        # If current_text exceeds chunk size, slice it
        while len(current_text) >= chunk_size_chars:
            chunk_slice = current_text[:chunk_size_chars]
            chunk_id = f"chk-{uuid.uuid4()}"
            token_est = max(1, len(chunk_slice) // 4)

            chunks.append(DocumentChunkModel(
                chunk_id=chunk_id,
                document_id=document_id,
                company_id=company_id,
                page_start=current_start_page,
                page_end=page.pdf_page_1based,
                section=current_section,
                text_content=chunk_slice.strip(),
                token_estimate=token_est
            ))

            # Advance with overlap
            current_text = current_text[chunk_size_chars - overlap_chars:]
            current_start_page = page.pdf_page_1based

    # Remainder chunk
    if current_text.strip():
        chunk_id = f"chk-{uuid.uuid4()}"
        chunks.append(DocumentChunkModel(
            chunk_id=chunk_id,
            document_id=document_id,
            company_id=company_id,
            page_start=current_start_page,
            page_end=pages[-1].pdf_page_1based if pages else 1,
            section=current_section,
            text_content=current_text.strip(),
            token_estimate=max(1, len(current_text) // 4)
        ))

    return chunks

class DocumentIndexer:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def index_document(
        self,
        document_id: str,
        company_id: str,
        pages: List[ParsedPage]
    ) -> int:
        """Stores pages and chunks, indexing text into SQLite FTS5 for primary source retrieval."""
        # 1. Store pages
        for page in pages:
            page_id = f"page-{document_id}-{page.pdf_page_1based}"
            self.conn.execute("""
                INSERT OR REPLACE INTO source_pages (
                    id, document_id, pdf_page_1based, printed_label,
                    text_content, ocr_flag, text_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                page_id, document_id, page.pdf_page_1based, page.printed_label,
                page.text, 1 if page.ocr_flag else 0, str(hash(page.text))
            ))

        # 2. Chunk pages
        chunks = chunk_document_pages(document_id, company_id, pages)

        # 3. Store chunks and insert into FTS5
        for chk in chunks:
            self.conn.execute("""
                INSERT OR REPLACE INTO document_chunks (
                    id, document_id, company_id, page_start, page_end,
                    section, text_content, token_estimate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chk.chunk_id, chk.document_id, chk.company_id, chk.page_start,
                chk.page_end, chk.section, chk.text_content, chk.token_estimate
            ))

            # Virtual FTS5 table
            self.conn.execute("""
                INSERT INTO chunks_fts (chunk_id, company_id, section, text_content)
                VALUES (?, ?, ?, ?)
            """, (chk.chunk_id, chk.company_id, chk.section, chk.text_content))

        self.conn.commit()
        return len(chunks)

    def search_chunks(
        self,
        company_id: str,
        query: str,
        limit: int = 8
    ) -> List[Dict[str, Any]]:
        """Searches document chunks using SQLite FTS5 porter-stemmed match."""
        # Clean query: strip special FTS syntax characters
        clean_query = re.sub(r"[^\w\s]", "", query).strip()
        if not clean_query:
            return []

        # Natural-language questions contain many terms that need not occur in
        # one short PDF chunk. Rank a union of substantive terms instead.
        tokens = [token for token in clean_query.split() if len(token) >= 3][:12]
        if not tokens:
            return []
        fts_query = " OR ".join(f'"{token}"' for token in tokens)

        rows = self.conn.execute("""
            SELECT c.id, c.document_id, c.company_id, c.page_start, c.page_end,
                   c.section, c.text_content, snippet(chunks_fts, 3, '<b>', '</b>', '...', 15) as snippet_text
            FROM chunks_fts f
            JOIN document_chunks c ON f.chunk_id = c.id
            WHERE chunks_fts MATCH ? AND f.company_id = ?
            ORDER BY bm25(chunks_fts)
            LIMIT ?
        """, (fts_query, company_id, limit)).fetchall()

        return [
            {
                "chunk_id": r["id"],
                "document_id": r["document_id"],
                "company_id": r["company_id"],
                "page_start": r["page_start"],
                "page_end": r["page_end"],
                "section": r["section"],
                "text_content": r["text_content"],
                "snippet": r["snippet_text"]
            }
            for r in rows
        ]

# Alias for backwards compatibility
FTSIndexer = DocumentIndexer

