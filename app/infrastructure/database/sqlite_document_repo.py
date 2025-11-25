"""SQLite Document Repository implementation."""
import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from app.domain.models import DocumentModel

class SQLiteDocumentRepository:
    def __init__(self, db_path: str = "data/resume_toolkit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_document(self, document: DocumentModel) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO documents (
                    application_id, profile_id, job_posting_id, document_type, title, content, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                document.application_id,
                document.profile_id,
                document.job_posting_id,
                document.document_type,
                document.title,
                document.content,
                document.created_at or datetime.utcnow()
            ))
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
        finally:
            conn.close()

    def get_document_by_id(self, document_id: int) -> Optional[DocumentModel]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return DocumentModel(
                id=row['id'],
                application_id=row['application_id'],
                profile_id=row['profile_id'],
                job_posting_id=row['job_posting_id'],
                document_type=row['document_type'],
                title=row['title'],
                content=row['content'],
                created_at=row['created_at']
            )
        finally:
            conn.close()

    def list_documents_for_profile(self, profile_id: int, doc_type: Optional[str] = None) -> List[DocumentModel]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if doc_type:
                cursor.execute("SELECT * FROM documents WHERE profile_id = ? AND document_type = ? ORDER BY created_at DESC", (profile_id, doc_type))
            else:
                cursor.execute("SELECT * FROM documents WHERE profile_id = ? ORDER BY created_at DESC", (profile_id,))
            docs = []
            for row in cursor.fetchall():
                docs.append(DocumentModel(
                    id=row['id'],
                    application_id=row['application_id'],
                    profile_id=row['profile_id'],
                    job_posting_id=row['job_posting_id'],
                    document_type=row['document_type'],
                    title=row['title'],
                    content=row['content'],
                    created_at=row['created_at']
                ))
            return docs
        finally:
            conn.close()

    def delete_document(self, document_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        finally:
            conn.close()
