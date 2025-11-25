"""
Document Service Interface
Defines contract for resume, cover letter, and document generation.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import DocumentGenerationRequest, DocumentModel

class IDocumentService(ABC):
    @abstractmethod
    def generate_document(self, request: DocumentGenerationRequest) -> DocumentModel:
        pass

    @abstractmethod
    def get_document(self, document_id: int) -> Optional[DocumentModel]:
        pass

    @abstractmethod
    def list_documents(self, profile_id: int, doc_type: Optional[str] = None) -> List[DocumentModel]:
        """List documents for a profile, optionally filtering by type."""
        pass

    @abstractmethod
    def delete_document(self, document_id: int) -> bool:
        pass
