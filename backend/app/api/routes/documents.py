"""Document upload and management routes."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ...database.database import get_db
from ...database.models import User, Document, DocumentStatus
from ...schemas.documents import DocumentResponse, DocumentListResponse
from ...services.document_service import document_service
from ...services.extraction_service import extraction_service
from ...services.vector_service import vector_service
from ...core.security import get_current_user, require_privacy_officer
from ...core.logging import logger
router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    doc = await document_service.upload_document(db, file, current_user.id, current_user.organization_id)
    background_tasks.add_task(process_document, doc.id, current_user.id)
    return DocumentResponse.model_validate(doc)

def process_document(document_id: int, user_id: int):
    """Background task: extract text from document."""
    from ...database.database import SessionLocal
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        file_path = document_service.upload_dir / doc.stored_filename
        text, method, confidence = extraction_service.extract(doc, file_path)
        
        doc.extracted_text = text
        doc.extraction_method = method
        doc.ocr_confidence = confidence

        vector_stored = False
        if text:
            # Store extracted text as vector chunks for RAG
            vector_stored = vector_service.add_document_chunks(
                document_id=doc.id,
                organization_id=doc.organization_id,
                filename=doc.original_filename,
                text=text,
            )

            if vector_stored:
                logger.info(
                    f"Document {document_id} indexed in ChromaDB successfully"
                )
            else:
                logger.warning(
                    f"Document {document_id} extracted but vector indexing failed"
                )

        doc.status = DocumentStatus.EXTRACTED if text else DocumentStatus.FAILED
        db.commit()

        logger.info(
            f"Document {document_id} extracted: {method} ({len(text)} chars)"
        )
    except Exception as e:
        logger.error(f"Document extraction failed: {e}")
        if doc:
            doc.status = DocumentStatus.FAILED
            db.commit()
    finally:
        db.close()

@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    docs = document_service.get_documents(db, current_user.organization_id)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in docs],
        total=len(docs),
    )

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = document_service.get_document(db, document_id, current_user.organization_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_privacy_officer),
):
    success = document_service.delete_document(
        db, document_id, current_user.organization_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "message": "Document deleted"}
