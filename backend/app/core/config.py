"""Application configuration with environment variable support."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/privacy_audit.db")

    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # File Upload
    UPLOAD_DIRECTORY: Path = BASE_DIR / "data" / "uploads"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".png", ".jpg", ".jpeg"}
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/csv",
        "text/plain",
        "image/png",
        "image/jpeg",
    }

    # AI / LLM
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: Path = Path(r"D:\PrivacyAuditChroma")

    # Reports
    REPORTS_DIRECTORY: Path = BASE_DIR / "data" / "reports"

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # App
    APP_NAME: str = "PrivacyAudit AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Demo
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() == "true"

settings = Settings()
