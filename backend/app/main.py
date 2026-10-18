"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import logger
from .database.database import init_db
from .api.routes import (
    auth, documents, analysis, findings, remediation,
    chat, reports, dashboard, health, data_inventory, audit
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PrivacyAudit AI...")
    init_db()
    yield
    logger.info("Shutting down PrivacyAudit AI...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Privacy Impact Assessment & DPDP Compliance Assistant",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix="/api/auth")
app.include_router(documents.router, prefix="/api/documents")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(findings.router, prefix="/api")
app.include_router(remediation.router, prefix="/api/remediation")
app.include_router(chat.router, prefix="/api")
app.include_router(reports.router, prefix="/api/reports")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(data_inventory.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(health.router, prefix="/api/health")

@app.get("/")
def root():
    return {
        "message": "PrivacyAudit AI API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
