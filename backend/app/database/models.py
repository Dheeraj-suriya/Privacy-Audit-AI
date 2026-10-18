"""SQLAlchemy ORM models for PrivacyAudit AI."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    PRIVACY_OFFICER = "PRIVACY_OFFICER"
    AUDITOR = "AUDITOR"
    EMPLOYEE = "EMPLOYEE"

class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AnalysisStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class FindingStatus(str, enum.Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class RemediationStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Priority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ControlStatus(str, enum.Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    NOT_ASSESSED = "NOT_ASSESSED"

# ─── Organization ────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="organization", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="organization", cascade="all, delete-orphan")
    processing_activities = relationship("ProcessingActivity", back_populates="organization", cascade="all, delete-orphan")
    data_flows = relationship("DataFlow", back_populates="organization", cascade="all, delete-orphan")
    remediation_tasks = relationship("RemediationTask", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")

# ─── User ────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")
    uploaded_documents = relationship("Document", back_populates="uploader")
    assigned_tasks = relationship("RemediationTask", back_populates="assignee")
    audit_logs = relationship("AuditLog", back_populates="user")

# ─── Document ────────────────────────────────────────────────────

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    extracted_text = Column(Text)
    extraction_method = Column(String(50))
    ocr_confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")

# ─── Analysis ────────────────────────────────────────────────────

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.QUEUED, nullable=False)
    compliance_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="analyses")
    organization = relationship("Organization", back_populates="analyses")
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")

# ─── Finding ─────────────────────────────────────────────────────

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    risk_score = Column(Float, default=0.0)
    status = Column(Enum(FindingStatus), default=FindingStatus.OPEN, nullable=False)
    evidence = Column(Text)
    evidence_document = Column(String(500))
    evidence_section = Column(String(500))
    control_id = Column(String(50))
    recommendation = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("Analysis", back_populates="findings")
    organization = relationship("Organization", back_populates="findings")
    reviewer = relationship("User")
    remediation_tasks = relationship("RemediationTask", back_populates="finding", cascade="all, delete-orphan")

# ─── Processing Activity ─────────────────────────────────────────

class ProcessingActivity(Base):
    __tablename__ = "processing_activities"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    purpose = Column(Text)
    data_subjects = Column(Text)
    data_categories = Column(Text)
    collection_source = Column(String(255))
    storage_location = Column(String(255))
    retention_period = Column(String(255))
    external_processors = Column(Text)
    cross_border_transfer = Column(Boolean, default=False)
    legal_basis = Column(String(255))
    risk_level = Column(Enum(Severity), default=Severity.LOW)
    owner = Column(String(255))
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="processing_activities")

# ─── Data Flow ───────────────────────────────────────────────────

class DataFlow(Base):
    __tablename__ = "data_flows"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    source = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    data_categories = Column(Text)
    purpose = Column(Text)
    risk_level = Column(Enum(Severity), default=Severity.LOW)
    retention_period = Column(String(255))
    deletion_mechanism = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="data_flows")

# ─── Remediation Task ────────────────────────────────────────────

class RemediationTask(Base):
    __tablename__ = "remediation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    status = Column(Enum(RemediationStatus), default=RemediationStatus.OPEN, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime(timezone=True))
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    finding = relationship("Finding", back_populates="remediation_tasks")
    organization = relationship("Organization", back_populates="remediation_tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

# ─── Compliance Control ──────────────────────────────────────────

class ComplianceControl(Base):
    __tablename__ = "compliance_controls"

    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    requirement = Column(Text)
    evidence_keywords = Column(Text)
    risk_if_missing = Column(Text)
    recommended_action = Column(Text)
    severity = Column(Enum(Severity), default=Severity.MEDIUM)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─── Report ──────────────────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    report_type = Column(String(50), default="pdf")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("Analysis", back_populates="reports")

# ─── Audit Log ───────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    metadata_json = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

# ─── Chat Conversation ───────────────────────────────────────────

class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON string of source references
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("ChatConversation", back_populates="messages")
