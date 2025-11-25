"""
FastAPI Document Router
Handles document generation and retrieval endpoints with full service integration.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
import os
import logging

from app.domain.models import DocumentGenerationRequest, DocumentModel, DocumentType
from app.application.services.document_service_impl import DocumentService
from app.infrastructure.database.sqlite_profile_repo import SQLiteProfileRepository
from app.infrastructure.database.sqlite_job_repo import SQLiteJobRepository
from app.infrastructure.database.sqlite_document_repo import SQLiteDocumentRepository
from app.infrastructure.event_bus.event_bus import EventBus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

class GenerateDocumentRequest(BaseModel):
    profile_id: int
    document_type: str  # resume | cover_letter | ats_report
    application_id: Optional[int] = None
    job_posting_id: Optional[int] = None
    title: Optional[str] = None
    custom_points: Optional[List[str]] = None


def get_document_service() -> DocumentService:
    """Create DocumentService instance with dependencies"""
    db_path = os.getenv("DATABASE_PATH", "data/resume_toolkit.db")
    profile_repo = SQLiteProfileRepository(db_path)
    job_repo = SQLiteJobRepository(db_path)
    document_repo = SQLiteDocumentRepository(db_path)
    event_bus = EventBus()
    return DocumentService(profile_repo, job_repo, document_repo, event_bus)

@router.post("/generate", status_code=status.HTTP_201_CREATED, response_model=DocumentModel)
async def generate_document(
    request: GenerateDocumentRequest,
    service: DocumentService = Depends(get_document_service)
):
    """Generate a new document (resume, cover_letter, ats_report)."""
    try:
        # Validate document type
        try:
            doc_type_enum = DocumentType(request.document_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid document_type: {request.document_type}")

        gen_req = DocumentGenerationRequest(
            profile_id=request.profile_id,
            application_id=request.application_id,
            job_posting_id=request.job_posting_id,
            document_type=doc_type_enum,
            title=request.title,
            custom_points=request.custom_points
        )
        document = service.generate_document(gen_req)
        logger.info(f"Generated document {document.id} of type {document.document_type} for profile {request.profile_id}")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate document: {str(e)}")

@router.get("/{document_id}", response_model=DocumentModel)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get a document by its ID."""
    try:
        doc = service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.get("/profile/{profile_id}", response_model=dict)
async def list_documents(
    profile_id: int,
    doc_type: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """List documents for a profile with optional type filter."""
    try:
        doc_type_enum = None
        if doc_type:
            try:
                doc_type_enum = DocumentType(doc_type.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid doc_type: {doc_type}")

        documents = service.list_documents(profile_id, doc_type_enum.value if doc_type_enum else None)
        return {"documents": documents, "total": len(documents), "filters": {"doc_type": doc_type}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents for profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document by ID."""
    try:
        success = service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        logger.info(f"Deleted document {document_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
