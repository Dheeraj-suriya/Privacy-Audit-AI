"""Document upload and management service."""
import os
import shutil
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from ..database.models import Document, DocumentStatus, AuditLog
from ..schemas.documents import DocumentResponse
from ..utils.file_utils import (
    validate_file, calculate_sha256, generate_secure_filename,
    get_file_type, sanitize_filename
)
from ..core.config import settings
from ..core.logging import logger

class DocumentService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIRECTORY
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_document(
        self, db: Session, file: UploadFile, user_id: int, organization_id: int
    ) -> Document:
        """Process and store an uploaded document securely."""

        # Validate
        is_valid, error = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

        # Generate secure filename
        original_name = sanitize_filename(file.filename)
        stored_name = generate_secure_filename(original_name)
        file_path = self.upload_dir / stored_name

        # Write file
        with open(file_path, "wb") as f:
            f.write(content)

        # Calculate hash
        sha256 = calculate_sha256(file_path)

        # Check for duplicate
        existing = db.query(Document).filter(
            Document.organization_id == organization_id,
            Document.sha256 == sha256
        ).first()
        if existing:
            os.remove(file_path)
            raise HTTPException(status_code=409, detail="Document already exists in this organization")

        # Create record
        doc = Document(
            organization_id=organization_id,
            uploaded_by=user_id,
            original_filename=original_name,
            stored_filename=stored_name,
            file_type=get_file_type(original_name),
            file_size=len(content),
            sha256=sha256,
            status=DocumentStatus.UPLOADED,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Audit log
        self._log_action(db, organization_id, user_id, "DOCUMENT_UPLOAD", "Document", doc.id)

        logger.info(f"Document uploaded: {doc.id} - {original_name}")
        return doc

    def get_documents(self, db: Session, organization_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        return db.query(Document).filter(
            Document.organization_id == organization_id
        ).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    def get_document(self, db: Session, document_id: int, organization_id: int) -> Optional[Document]:
        return db.query(Document).filter(
            Document.id == document_id,
            Document.organization_id == organization_id
        ).first()

    def delete_document(self, db: Session, document_id: int, organization_id: int, user_id: int) -> bool:
        doc = self.get_document(db, document_id, organization_id)
        if not doc:
            return False

        # Remove file
        file_path = self.upload_dir / doc.stored_filename
        if file_path.exists():
            os.remove(file_path)

        db.delete(doc)
        db.commit()

        self._log_action(db, organization_id, user_id, "DOCUMENT_DELETE", "Document", document_id)
        logger.info(f"Document deleted: {document_id}")
        return True

    def update_status(self, db: Session, document_id: int, status: DocumentStatus):
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = status
            db.commit()

    def _log_action(self, db: Session, org_id: int, user_id: int, action: str, resource_type: str, resource_id: int):
        log = AuditLog(
            organization_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        db.add(log)
        db.commit()

document_service = DocumentService()
