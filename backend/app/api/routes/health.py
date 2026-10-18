"""Health check routes."""
from fastapi import APIRouter
from ...services.llm_service import llm_service
from ...services.vector_service import vector_service

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ollama_available": llm_service.ai_available,
        "chromadb_available": vector_service.is_available(),
        "message": "PrivacyAudit AI is running",
    }
