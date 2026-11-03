"""
app/services/document_processor.py

Document processing pipeline:
1. Extract text
2. Split text into chunks
3. Generate embeddings
4. Save DocumentChunk rows
"""

from __future__ import annotations

import csv
from pathlib import Path

import tiktoken
from docx import Document as DocxDocument
from pypdf import PdfReader
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.gemini_provider import GeminiEmbeddingProvider
from app.config import settings
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk


def extract_text(file_path: str, file_type: str) -> list[tuple[str, int | None]]:
    """
    Extract text from a supported document.

    Returns:
        list of (text, page_number)
    """

    path = Path(file_path)

    if file_type == "PDF":
        reader = PdfReader(str(path))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                pages.append((text, page_number))

        return pages

    if file_type == "DOCX":
        doc = DocxDocument(str(path))

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        )

        return [(text, None)]

    if file_type in {"TXT", "MD"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return [(text, None)]

    if file_type == "CSV":
        rows = []

        with path.open("r", encoding="utf-8", errors="ignore", newline="") as file:
            reader = csv.reader(file)

            for row in reader:
                rows.append(" | ".join(row))

        return [("\n".join(rows), None)]

    raise ValueError(f"Unsupported file type: {file_type}")


def clean_text(text: str) -> str:
    """Basic text cleanup."""

    lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


def chunk_text(
    text: str,
    page_number: int | None = None,
) -> list[dict]:
    """
    Split text using the configured token size and overlap.
    """

    if not text.strip():
        return []

    encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)

    chunk_size = settings.chunk_size_tokens
    overlap = settings.chunk_overlap_tokens

    if overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))

        chunk_tokens = tokens[start:end]
        chunk_content = encoding.decode(chunk_tokens).strip()

        if chunk_content:
            chunks.append(
                {
                    "content": chunk_content,
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "token_count": len(chunk_tokens),
                }
            )

            chunk_index += 1

        if end >= len(tokens):
            break

        start = end - overlap

    return chunks


async def process_document(
    db: AsyncSession,
    document: Document,
) -> int:
    """
    Process a document and create its embeddings.

    Returns:
        Number of chunks created.
    """

    document.status = DocumentStatus.PROCESSING
    document.error_message = None

    await db.flush()

    try:
        extracted_pages = extract_text(
            document.storage_path,
            document.file_type.value,
        )

        all_chunks = []

        for text, page_number in extracted_pages:
            cleaned = clean_text(text)

            if not cleaned:
                continue

            page_chunks = chunk_text(
                cleaned,
                page_number=page_number,
            )

            all_chunks.extend(page_chunks)

        if not all_chunks:
            raise ValueError(
                "No readable text could be extracted from the document."
            )

        embedding_provider = GeminiEmbeddingProvider()

        texts = [chunk["content"] for chunk in all_chunks]

        embeddings = await embedding_provider.generate_embeddings_batch(texts)

        if len(embeddings) != len(all_chunks):
            raise ValueError(
                "Embedding count does not match chunk count."
            )

        # Remove old chunks if this document is being reprocessed.
        await db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document.id
            )
        )

        for chunk, embedding_response in zip(
            all_chunks,
            embeddings,
            strict=True,
        ):
            db_chunk = DocumentChunk(
                company_id=document.company_id,
                document_id=document.id,
                content=chunk["content"],
                embedding=embedding_response.embedding,
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                token_count=chunk["token_count"],
                chunk_metadata={
                    "embedding_model": embedding_response.model,
                },
            )

            db.add(db_chunk)

        document.chunk_count = len(all_chunks)
        document.status = DocumentStatus.READY
        document.error_message = None

        await db.commit()

        return len(all_chunks)

    except Exception as exc:
        await db.rollback()

        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)

        await db.commit()

        raise