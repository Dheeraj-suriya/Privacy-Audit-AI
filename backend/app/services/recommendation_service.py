"""Remediation recommendation engine."""
from typing import List, Dict, Any, Optional

from ..core.logging import logger

class RecommendationService:
    """Generate actionable remediation recommendations."""

    def generate_from_finding(self, finding: Dict[str, Any]) -> str:
        """Generate recommendation for a specific finding."""
        category = finding.get("category", "")
        control_id = finding.get("control_id", "")

        # Category-specific recommendations
        recommendations = {
            "Transparency": (
                "1. Draft a comprehensive privacy notice covering all processing activities. "
                "2. Include data subject rights, contact details, and complaint mechanisms. "
                "3. Publish the notice prominently and maintain version control."
            ),
            "Processing": (
                "1. Document specific, explicit purposes for each processing activity. "
                "2. Review data inventory to eliminate unnecessary collection. "
                "3. Implement purpose limitation checks in system design."
            ),
            "Retention": (
                "1. Define retention periods for each data category aligned with legal/business needs. "
                "2. Implement automated deletion or anonymization workflows. "
                "3. Document retention schedules and review annually."
            ),
            "Security": (
                "1. Implement encryption at rest and in transit. "
                "2. Deploy role-based access controls and MFA. "
                "3. Establish security monitoring, logging, and incident response."
            ),
            "Third Parties": (
                "1. Inventory all third-party processors. "
                "2. Execute Data Processing Agreements with adequate safeguards. "
                "3. Conduct due diligence and periodic audits of processors."
            ),
            "Transfer": (
                "1. Map all cross-border data flows. "
                "2. Identify and document appropriate transfer mechanisms. "
                "3. Assess adequacy decisions or implement Standard Contractual Clauses."
            ),
            "Consent": (
                "1. Implement granular, opt-in consent mechanisms. "
                "2. Ensure consent is freely given, specific, informed, and unambiguous. "
                "3. Provide easy withdrawal mechanism and maintain consent records."
            ),
            "Rights": (
                "1. Establish procedures for access, correction, erasure, and portability requests. "
                "2. Define response timelines and responsible teams. "
                "3. Maintain request tracking and outcome documentation."
            ),
            "Incident Response": (
                "1. Implement breach detection and assessment procedures. "
                "2. Define notification timelines: authority within 72 hours, data subjects without delay. "
                "3. Conduct regular breach response drills."
            ),
            "Special Categories": (
                "1. Inventory all sensitive personal data categories. "
                "2. Implement enhanced technical and organizational measures. "
                "3. Ensure specific legal basis exists for processing sensitive data."
            ),
        }

        return recommendations.get(category, (
            "1. Review the identified gap against applicable privacy requirements. "
            "2. Develop and document appropriate controls. "
            "3. Assign ownership and establish review cycles."
        ))

    def generate_from_risk(self, risk_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on risk factors."""
        recommendations = []

        for factor in risk_result.get("factors", []):
            if factor["score"] > factor["weight"] * 0.5:  # Score > 50% of weight
                rec = self._factor_recommendation(factor)
                if rec:
                    recommendations.append(rec)

        return recommendations

    def _factor_recommendation(self, factor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map risk factor to recommendation."""
        factor_map = {
            "sensitive_data": {
                "title": "Sensitive Data Inventory and Protection",
                "action": "Conduct a comprehensive inventory of sensitive personal data and implement category-specific enhanced controls.",
                "priority": "HIGH",
            },
            "external_sharing": {
                "title": "Third-Party Data Sharing Assessment",
                "action": "Map all external data sharing, execute DPAs, and verify processor security controls.",
                "priority": "HIGH",
            },
            "retention_gap": {
                "title": "Data Retention Policy Development",
                "action": "Define and implement retention schedules with automated deletion mechanisms.",
                "priority": "MEDIUM",
            },
            "security_gap": {
                "title": "Security Control Enhancement",
                "action": "Implement encryption, access controls, MFA, and security monitoring.",
                "priority": "CRITICAL",
            },
            "evidence_gap": {
                "title": "Compliance Documentation Improvement",
                "action": "Strengthen documentation for failed/partial controls with evidence collection.",
                "priority": "MEDIUM",
            },
            "cross_border": {
                "title": "Cross-Border Transfer Assessment",
                "action": "Document legal basis for all international transfers and implement appropriate safeguards.",
                "priority": "HIGH",
            },
        }

        return factor_map.get(factor["name"])

recommendation_service = RecommendationService()
