"""PDF and other format report generation."""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.config import settings
from ..core.logging import logger

class ReportService:
    """Generate professional audit reports."""

    def __init__(self):
        self.reports_dir = settings.REPORTS_DIRECTORY
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf_report(
        self,
        analysis_id: int,
        organization_id: int,
        organization_name: str,
        findings: List[Dict],
        compliance_results: List[Dict],
        risk_result: Dict,
        score_data: Dict,
        processing_activities: List[Dict],
        data_flows: List[Dict],
        pii_summary: Dict,
    ) -> str:
        """Generate a professional PDF audit report."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            filename = f"privacy_audit_report_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.reports_dir / filename

            doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=18)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#1e3a5f'),
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#2c5282'),
            )

            story = []

            # Cover Page
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("PrivacyAudit AI", title_style))
            story.append(Paragraph("Privacy Impact Assessment Report", styles["Heading2"]))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"<b>Organization:</b> {organization_name}", styles["Normal"]))
            story.append(Paragraph(f"<b>Assessment Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
            story.append(Paragraph(f"<b>Assessment ID:</b> {analysis_id}", styles["Normal"]))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(
                "<i>This assessment is generated using automated rules, document analysis, and AI-assisted reasoning. "
                "It is intended to support privacy and compliance review and does not constitute legal advice or a "
                "definitive determination of compliance. Professional/legal review is recommended.</i>",
                styles["Italic"]
            ))
            story.append(PageBreak())

            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Paragraph(f"Overall Privacy Score: <b>{score_data.get('score', 0)}/100</b>", styles["Normal"]))
            story.append(Paragraph(f"Risk Level: <b>{risk_result.get('severity', 'Unknown')}</b>", styles["Normal"]))
            story.append(Paragraph(f"Total Findings: <b>{len(findings)}</b>", styles["Normal"]))
            story.append(Spacer(1, 0.2*inch))

            # Risk Distribution
            risk_dist = risk_result.get("risk_distribution", {})
            risk_data = [
                ["Severity", "Count"],
                ["Critical", str(risk_dist.get("CRITICAL", 0))],
                ["High", str(risk_dist.get("HIGH", 0))],
                ["Medium", str(risk_dist.get("MEDIUM", 0))],
                ["Low", str(risk_dist.get("LOW", 0))],
            ]
            risk_table = Table(risk_data, colWidths=[2*inch, 1.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(risk_table)
            story.append(PageBreak())

            # Findings
            story.append(Paragraph("Findings", heading_style))
            for finding in findings[:20]:  # Limit to 20 findings
                story.append(Paragraph(f"<b>{finding.get('title', 'Untitled')}</b>", styles["Heading3"]))
                story.append(Paragraph(f"Severity: {finding.get('severity', 'Unknown')} | Score: {finding.get('risk_score', 0)}", styles["Normal"]))
                story.append(Paragraph(f"Description: {finding.get('description', '')}", styles["Normal"]))
                story.append(Paragraph(f"Recommendation: {finding.get('recommendation', '')}", styles["Normal"]))
                story.append(Spacer(1, 0.1*inch))

            # Compliance Assessment
            story.append(PageBreak())
            story.append(Paragraph("Compliance Assessment", heading_style))
            for result in compliance_results:
                status_color = {"PASS": "green", "PARTIAL": "orange", "FAIL": "red", "NOT_ASSESSED": "gray"}
                color = status_color.get(result.get("status"), "black")
                story.append(Paragraph(
                    f"<b>{result.get('control_id', '')}</b> — {result.get('title', '')} "
                    f"(<font color='{color}'>{result.get('status', '')}</font>)",
                    styles["Normal"]
                ))
                story.append(Paragraph(f"Explanation: {result.get('explanation', '')}", styles["Normal"]))
                story.append(Spacer(1, 0.1*inch))

            # Limitations
            story.append(PageBreak())
            story.append(Paragraph("Limitations", heading_style))
            story.append(Paragraph(
                "This report is generated using automated rules, natural language processing, and optional AI-assisted reasoning. "
                "Results should be reviewed by qualified privacy professionals. The assessment does not constitute legal advice. "
                "Controls are configurable criteria rather than definitive legal determinations. "
                "False positives and negatives may occur. Organization-specific context may require manual review.",
                styles["Normal"]
            ))

            doc.build(story)
            logger.info(f"PDF report generated: {filepath}")
            return str(filepath)

        except ImportError:
            logger.warning("reportlab not available — generating text report instead")
            return self._generate_text_report(
                analysis_id, organization_id, organization_name,
                findings, compliance_results, risk_result, score_data
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return self._generate_text_report(
                analysis_id, organization_id, organization_name,
                findings, compliance_results, risk_result, score_data
            )

    def _generate_text_report(self, analysis_id, org_id, org_name, findings, compliance, risk, score) -> str:
        """Fallback text report."""
        filename = f"privacy_audit_report_{analysis_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.reports_dir / filename

        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("PrivacyAudit AI — Privacy Impact Assessment Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Organization: {org_name}\n")
            f.write(f"Assessment ID: {analysis_id}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"Privacy Score: {score.get('score', 0)}/100\n")
            f.write(f"Risk Level: {risk.get('severity', 'Unknown')}\n\n")
            f.write("FINDINGS\n")
            f.write("-" * 80 + "\n")
            for finding in findings:
                f.write(f"[{finding.get('severity')}] {finding.get('title')}\n")
                f.write(f"  {finding.get('description')}\n")
                f.write(f"  Recommendation: {finding.get('recommendation')}\n\n")
            f.write("\nDISCLAIMER: This is an AI-assisted assessment, not legal advice.\n")

        return str(filepath)

    def get_report_path(self, filename: str) -> Path:
        return self.reports_dir / filename

report_service = ReportService()
