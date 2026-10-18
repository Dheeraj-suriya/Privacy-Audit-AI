"""Document analysis pipeline orchestration."""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..database.models import (
    Document, Analysis, Finding, AnalysisStatus, DocumentStatus,
    ProcessingActivity, DataFlow, ComplianceControl, AuditLog, Severity, FindingStatus
)
from ..database.database import SessionLocal
from ..core.logging import logger
from ..services.extraction_service import extraction_service
from ..services.pii_detection_service import pii_detection_service
from ..services.compliance_service import compliance_service
from ..services.risk_engine import risk_engine
from ..services.recommendation_service import recommendation_service
from ..services.data_mapping_service import data_mapping_service
from ..services.llm_service import llm_service
from ..services.vector_service import vector_service

class AnalysisService:
    """Orchestrate the complete privacy analysis pipeline."""

    def start_analysis(self, db: Session, document_id: int, user_id: int) -> Analysis:
        """Start a new analysis job."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        # Create analysis record
        analysis = Analysis(
            document_id=document_id,
            organization_id=document.organization_id,
            status=AnalysisStatus.QUEUED,
            started_at=datetime.utcnow(),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Update document status
        document.status = DocumentStatus.ANALYZING
        db.commit()

        logger.info(f"Analysis {analysis.id} queued for document {document_id}")
        return analysis

    def run_analysis(self, db: Session, analysis_id: int) -> Analysis:
        """Execute the full analysis pipeline."""
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError("Analysis not found")

        document = db.query(Document).filter(Document.id == analysis.document_id).first()
        if not document or not document.extracted_text:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = "Document has no extracted text"
            db.commit()
            return analysis

        try:
            analysis.status = AnalysisStatus.PROCESSING
            db.commit()

            text = document.extracted_text

            # Step 1: PII Detection
            logger.info(f"Analysis {analysis_id}: PII detection")
            pii_results = pii_detection_service.detect(text, document.id)

            # Step 2: Compliance Assessment
            logger.info(f"Analysis {analysis_id}: Compliance assessment")
            compliance_results = compliance_service.assess(text, pii_results)

            # Step 3: Risk Calculation
            logger.info(f"Analysis {analysis_id}: Risk calculation")
            risk_result = risk_engine.calculate_risk(pii_results, compliance_results, text)

            # Step 4: Score Calculation
            logger.info(f"Analysis {analysis_id}: Score calculation")
            score_data = compliance_service.calculate_score(compliance_results)

            # Step 5: Data Mapping
            logger.info(f"Analysis {analysis_id}: Data mapping")
            activities = data_mapping_service.extract_processing_activities(text)
            flows = data_mapping_service.extract_data_flows(text)

            # Step 6: LLM Enhancement (optional)
            llm_enhancement = llm_service.analyze_document(text)

            # Step 7: Store vectors for RAG
            logger.info(f"Analysis {analysis_id}: Vector storage")
            vector_service.add_document_chunks(
                document_id=document.id,
                organization_id=document.organization_id,
                filename=document.original_filename,
                text=text,
            )

            # Step 8: Create findings
            logger.info(f"Analysis {analysis_id}: Creating findings")
            self._create_findings(db, analysis, compliance_results, risk_result, pii_results)

            # Step 9: Store processing activities
            self._store_activities(db, document.organization_id, activities)

            # Step 10: Store data flows
            self._store_flows(db, document.organization_id, flows)

            # Update analysis
            analysis.compliance_score = score_data["score"]
            analysis.risk_score = risk_result["risk_score"]
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            db.commit()

            # Update document status
            document.status = DocumentStatus.COMPLETED
            db.commit()

            logger.info(f"Analysis {analysis_id} completed successfully")

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
            document.status = DocumentStatus.FAILED
            db.commit()

        return analysis

    def _create_findings(self, db: Session, analysis: Analysis, 
                         compliance_results: List, risk_result: Dict, pii_results: Dict):
        """Create findings from compliance and risk results."""

        # Findings from compliance failures
        for result in compliance_results:
            if result.status in ["FAIL", "PARTIAL"]:
                severity = result.severity if result.status == "FAIL" else "MEDIUM"

                finding = Finding(
                    analysis_id=analysis.id,
                    organization_id=analysis.organization_id,
                    title=f"{result.control_id}: {result.title}",
                    description=result.explanation,
                    category=result.category,
                    severity=Severity(severity),
                    risk_score=result.confidence * 100,
                    status=FindingStatus.OPEN,
                    evidence=result.evidence[:1000],
                    evidence_document=analysis.document.original_filename,
                    control_id=result.control_id,
                    recommendation=result.recommendation,
                )
                db.add(finding)

        # Findings from risk factors
        for factor in risk_result.get("factors", []):
            if factor["score"] > factor["weight"] * 0.6:
                rec = recommendation_service._factor_recommendation(factor)
                if rec:
                    finding = Finding(
                        analysis_id=analysis.id,
                        organization_id=analysis.organization_id,
                        title=rec["title"],
                        description=factor["description"],
                        category="Risk",
                        severity=Severity(rec["priority"]),
                        risk_score=factor["score"] / factor["weight"] * 100,
                        status=FindingStatus.OPEN,
                        evidence=f"Risk factor: {factor['name']} scored {factor['score']}/{factor['weight']}",
                        evidence_document=analysis.document.original_filename,
                        recommendation=rec["action"],
                    )
                    db.add(finding)

        # Findings from PII detection
        if pii_results.get("categories", {}).get("Government ID", 0) > 0:
            finding = Finding(
                analysis_id=analysis.id,
                organization_id=analysis.organization_id,
                title="Government Identifiers Detected",
                description=f"Document contains {pii_results['categories']['Government ID']} potential government identifier references. Enhanced controls required.",
                category="Special Categories",
                severity=Severity.HIGH,
                risk_score=75,
                status=FindingStatus.OPEN,
                evidence="PII detection identified government ID patterns",
                evidence_document=analysis.document.original_filename,
                recommendation="Implement enhanced protections for government identifiers. Ensure specific legal basis exists. Apply encryption and strict access controls.",
            )
            db.add(finding)

        db.commit()

    def _store_activities(self, db: Session, org_id: int, activities: List[Dict]):
        """Store extracted processing activities."""
        for act in activities:
            activity = ProcessingActivity(
                organization_id=org_id,
                name=act["name"],
                purpose=act.get("purpose"),
                data_subjects=act.get("data_subjects"),
                data_categories=act.get("data_categories"),
                collection_source=act.get("collection_source"),
                storage_location=act.get("storage_location"),
                retention_period=act.get("retention_period"),
                external_processors=act.get("external_processors"),
                cross_border_transfer=act.get("cross_border_transfer", False),
                legal_basis=act.get("legal_basis"),
                risk_level=Severity(act.get("risk_level", "MEDIUM")),
                owner=act.get("owner"),
            )
            db.add(activity)
        db.commit()

    def _store_flows(self, db: Session, org_id: int, flows: List[Dict]):
        """Store extracted data flows."""
        for flow in flows:
            data_flow = DataFlow(
                organization_id=org_id,
                source=flow["source"],
                destination=flow["destination"],
                data_categories=flow.get("data_categories"),
                purpose=flow.get("purpose"),
                risk_level=Severity(flow.get("risk_level", "MEDIUM")),
            )
            db.add(data_flow)
        db.commit()

    def get_analysis(self, db: Session, analysis_id: int, org_id: int) -> Optional[Analysis]:
        return db.query(Analysis).filter(
            Analysis.id == analysis_id,
            Analysis.organization_id == org_id
        ).first()

    def get_analyses(self, db: Session, org_id: int, skip: int = 0, limit: int = 100) -> List[Analysis]:
        return db.query(Analysis).filter(
            Analysis.organization_id == org_id
        ).order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()

analysis_service = AnalysisService()
