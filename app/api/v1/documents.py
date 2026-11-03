"""
app/api/v1/documents.py

Document upload and management.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import CompanyUser
from app.db.session import get_db
from app.models.document import Document, FileType
from app.services.document_processor import process_document


router = APIRouter()


def get_file_type(filename: str) -> FileType:
    """Determine document type from file extension."""

    extension = Path(filename).suffix.lower().lstrip(".")

    mapping = {
        "pdf": FileType.PDF,
        "docx": FileType.DOCX,
        "txt": FileType.TXT,
        "csv": FileType.CSV,
        "md": FileType.MD,
    }

    file_type = mapping.get(extension)

    if file_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '.{extension}'. "
                f"Allowed types: {', '.join(settings.allowed_file_types)}"
            ),
        )

    return file_type


@router.post("/upload", summary="Upload a document to the knowledge base")
async def upload_document(
    current_user: CompanyUser,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and immediately process a document."""

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    file_type = get_file_type(file.filename)

    # Read the uploaded file.
    file_data = await file.read()

    max_size = settings.max_file_size_mb * 1024 * 1024

    if len(file_data) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File is too large. Maximum size is "
                f"{settings.max_file_size_mb} MB."
            ),
        )

    # Create company-specific storage directory.
    company_dir = (
        Path(settings.storage_path)
        / str(current_user.company_id)
    )

    company_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Generate unique stored filename.
    stored_filename = f"{uuid.uuid4()}_{file.filename}"

    storage_path = company_dir / stored_filename

    storage_path.write_bytes(file_data)

    # Create database record.
    document = Document(
        company_id=current_user.company_id,
        uploaded_by=current_user.id,
        filename=stored_filename,
        original_filename=file.filename,
        file_type=file_type,
        storage_path=str(storage_path),
        file_size_bytes=len(file_data),
    )

    db.add(document)

    await db.commit()
    await db.refresh(document)

    # Process immediately.
    try:
        chunk_count = await process_document(
            db=db,
            document=document,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {exc}",
        ) from exc

    return {
        "id": str(document.id),
        "filename": document.original_filename,
        "file_type": document.file_type.value,
        "status": document.status.value,
        "chunk_count": chunk_count,
        "file_size_bytes": document.file_size_bytes,
    }


@router.get("/", summary="List documents in current company")
async def list_documents(
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .where(Document.company_id == current_user.company_id)
        .order_by(Document.created_at.desc())
    )

    documents = result.scalars().all()

    return [
        {
            "id": str(document.id),
            "filename": document.original_filename,
            "file_type": document.file_type.value,
            "status": document.status.value,
            "chunk_count": document.chunk_count,
            "file_size_bytes": document.file_size_bytes,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{document_id}", summary="Get document details")
async def get_document(
    document_id: str,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == uuid.UUID(document_id),
            Document.company_id == current_user.company_id,
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return {
        "id": str(document.id),
        "filename": document.original_filename,
        "file_type": document.file_type.value,
        "status": document.status.value,
        "chunk_count": document.chunk_count,
        "file_size_bytes": document.file_size_bytes,
        "version": document.version,
        "title": document.title,
        "description": document.description,
        "error_message": document.error_message,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
    }


@router.delete("/{document_id}", summary="Delete a document")
async def delete_document(
    document_id: str,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == uuid.UUID(document_id),
            Document.company_id == current_user.company_id,
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    storage_path = Path(document.storage_path)

    if storage_path.exists():
        storage_path.unlink()

    await db.delete(document)
    await db.commit()

    return {
        "message": "Document deleted successfully.",
        "id": document_id,
    }


@router.post(
    "/{document_id}/reprocess",
    summary="Reprocess document",
)
async def reprocess_document(
    document_id: str,
    current_user: CompanyUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == uuid.UUID(document_id),
            Document.company_id == current_user.company_id,
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    try:
        chunk_count = await process_document(
            db=db,
            document=document,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {exc}",
        ) from exc

    return {
        "id": str(document.id),
        "status": document.status.value,
        "chunk_count": chunk_count,
    }