"""DPDP Compliance rule engine with configurable controls."""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.logging import logger
from ..core.config import settings

@dataclass
class ComplianceResult:
    control_id: str
    title: str
    category: str
    status: str  # PASS, PARTIAL, FAIL, NOT_ASSESSED
    evidence: str
    explanation: str
    recommendation: str
    severity: str
    confidence: float

class ComplianceService:
    """Configurable compliance rule engine."""

    def __init__(self):
        self.controls = self._load_controls()
        logger.info(f"Loaded {len(self.controls)} compliance controls")

    def _load_controls(self) -> List[Dict[str, Any]]:
        """Load controls from JSON file or use defaults."""
        controls_path = Path(__file__).parent.parent / "rules" / "dpdp_controls.json"

        if controls_path.exists():
            with open(controls_path, "r") as f:
                return json.load(f)

        # Default controls
        return self._default_controls()

    def _default_controls(self) -> List[Dict[str, Any]]:
        """Default DPDP-inspired controls."""
        return [
            {
                "control_id": "DPDP-001",
                "title": "Notice and Transparency",
                "category": "Transparency",
                "description": "Organization must provide clear notice about data processing",
                "requirement": "Privacy notice must describe purpose, data categories, and rights",
                "evidence_keywords": ["privacy notice", "privacy policy", "data subject rights", "transparency", "purpose"],
                "risk_if_missing": "Potential transparency gap — data subjects may not be informed",
                "recommended_action": "Review and publish a comprehensive privacy notice",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-002",
                "title": "Purpose Limitation",
                "category": "Processing",
                "description": "Personal data must be collected for specified, explicit, and legitimate purposes",
                "requirement": "Documented purpose for each processing activity",
                "evidence_keywords": ["purpose", "processing purpose", "legitimate purpose", "specified purpose"],
                "risk_if_missing": "Risk of unauthorized or excessive processing",
                "recommended_action": "Define and document specific purposes for all processing activities",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-003",
                "title": "Data Minimization",
                "category": "Processing",
                "description": "Only collect personal data that is necessary for the purpose",
                "requirement": "Evidence that data collection is limited to what is necessary",
                "evidence_keywords": ["minimization", "necessary", "minimal", "required only", "essential data"],
                "risk_if_missing": "Excessive data collection increases breach impact",
                "recommended_action": "Review data inventory and eliminate unnecessary data collection",
                "severity": "MEDIUM",
                "enabled": True,
            },
            {
                "control_id": "DPDP-004",
                "title": "Retention and Deletion",
                "category": "Retention",
                "description": "Personal data must not be retained longer than necessary",
                "requirement": "Documented retention periods and deletion procedures",
                "evidence_keywords": ["retention", "retain", "delete", "deletion", "erase", "storage period", "retention policy"],
                "risk_if_missing": "Data retained indefinitely increases exposure risk",
                "recommended_action": "Define retention periods and implement automated deletion",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-005",
                "title": "Security Safeguards",
                "category": "Security",
                "description": "Appropriate technical and organizational measures must protect personal data",
                "requirement": "Documented security controls: encryption, access control, monitoring",
                "evidence_keywords": ["encryption", "access control", "security", "safeguard", "protect", "secure", "auth"],
                "risk_if_missing": "Inadequate security increases breach likelihood",
                "recommended_action": "Implement encryption, access controls, and security monitoring",
                "severity": "CRITICAL",
                "enabled": True,
            },
            {
                "control_id": "DPDP-006",
                "title": "Third-Party Processor Management",
                "category": "Third Parties",
                "description": "Processors must be governed by contracts with adequate safeguards",
                "requirement": "Data processing agreements with all third-party processors",
                "evidence_keywords": ["processor", "third party", "vendor", "agreement", "contract", "dpa", "subprocessor"],
                "risk_if_missing": "Lack of contractual safeguards with processors",
                "recommended_action": "Execute data processing agreements with all vendors handling personal data",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-007",
                "title": "Cross-Border Transfer Controls",
                "category": "Transfer",
                "description": "Cross-border transfers require adequate protection mechanisms",
                "requirement": "Documented transfer mechanism: adequacy, SCCs, or consent",
                "evidence_keywords": ["cross border", "transfer", "international", "adequacy", "scc", "binding corporate"],
                "risk_if_missing": "Uncontrolled cross-border transfers may violate regulations",
                "recommended_action": "Assess and document legal basis for all cross-border transfers",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-008",
                "title": "Consent Management",
                "category": "Consent",
                "description": "Consent must be freely given, specific, informed, and unambiguous",
                "requirement": "Evidence of consent mechanism: granular, withdrawable, documented",
                "evidence_keywords": ["consent", "opt in", "agree", "permission", "withdraw", "granular"],
                "risk_if_missing": "Processing without valid legal basis",
                "recommended_action": "Implement granular, documented consent with withdrawal mechanism",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-009",
                "title": "Data Subject Rights",
                "category": "Rights",
                "description": "Mechanisms must exist for access, correction, erasure, and portability",
                "requirement": "Documented procedures for handling data subject requests",
                "evidence_keywords": ["access request", "correction", "erasure", "portability", "right to", "dsr", "data subject"],
                "risk_if_missing": "Inability to comply with data subject rights requests",
                "recommended_action": "Establish procedures and timelines for all data subject rights",
                "severity": "MEDIUM",
                "enabled": True,
            },
            {
                "control_id": "DPDP-010",
                "title": "Breach Notification",
                "category": "Incident Response",
                "description": "Data breaches must be detected, assessed, and notified appropriately",
                "requirement": "Breach detection, assessment, and notification procedures",
                "evidence_keywords": ["breach", "incident", "notification", "72 hours", "authority", "data breach"],
                "risk_if_missing": "Delayed or missed breach notification obligations",
                "recommended_action": "Implement breach detection and response procedures with notification timelines",
                "severity": "CRITICAL",
                "enabled": True,
            },
            {
                "control_id": "DPDP-011",
                "title": "Children\'s Data Protection",
                "category": "Special Categories",
                "description": "Enhanced protections for children\'s personal data",
                "requirement": "Age verification and parental consent mechanisms",
                "evidence_keywords": ["child", "minor", "under 18", "parental", "guardian", "age verification"],
                "risk_if_missing": "Processing children\'s data without adequate safeguards",
                "recommended_action": "Implement age verification and parental consent where applicable",
                "severity": "HIGH",
                "enabled": True,
            },
            {
                "control_id": "DPDP-012",
                "title": "Sensitive Personal Data",
                "category": "Special Categories",
                "description": "Sensitive data requires heightened protections and specific legal basis",
                "requirement": "Identification and enhanced controls for sensitive data categories",
                "evidence_keywords": ["sensitive", "health", "biometric", "genetic", "financial", "religion", "caste"],
                "risk_if_missing": "Inadequate protection for high-risk data categories",
                "recommended_action": "Inventory sensitive data and implement enhanced controls",
                "severity": "CRITICAL",
                "enabled": True,
            },
        ]

    def assess(self, text: str, pii_results: Dict[str, Any]) -> List[ComplianceResult]:
        """
        Assess document against compliance controls.
        Returns list of compliance results.
        """
        text_lower = text.lower()
        results = []

        for control in self.controls:
            if not control.get("enabled", True):
                continue

            # Match evidence keywords
            keywords = control.get("evidence_keywords", [])
            matches = []
            match_positions = []

            for keyword in keywords:
                for match in re.finditer(re.escape(keyword), text_lower):
                    matches.append(keyword)
                    # Extract snippet
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    snippet = text[start:end].strip()
                    match_positions.append(snippet)

            # Determine status based on evidence strength
            unique_matches = len(set(matches))
            total_keywords = len(keywords)

            if unique_matches == 0:
                status = "FAIL"
                confidence = 0.9
            elif unique_matches >= total_keywords * 0.7:
                status = "PASS"
                confidence = 0.85
            elif unique_matches >= total_keywords * 0.3:
                status = "PARTIAL"
                confidence = 0.75
            else:
                status = "FAIL"
                confidence = 0.8

            # Contextual adjustments based on PII findings
            if control["control_id"] == "DPDP-012" and pii_results.get("categories", {}).get("Government ID", 0) > 0:
                if status == "PASS":
                    status = "PARTIAL"  # Have sensitive data but need explicit controls
                    confidence = 0.7

            evidence_snippet = match_positions[0] if match_positions else "No direct evidence found in document"

            result = ComplianceResult(
                control_id=control["control_id"],
                title=control["title"],
                category=control["category"],
                status=status,
                evidence=evidence_snippet,
                explanation=self._generate_explanation(control, status, unique_matches, total_keywords),
                recommendation=control["recommended_action"],
                severity=control["severity"],
                confidence=confidence,
            )
            results.append(result)

        return results

    def _generate_explanation(self, control: Dict, status: str, matches: int, total: int) -> str:
        """Generate human-readable explanation."""
        if status == "PASS":
            return f"Document provides strong evidence for '{control['title']}'. Found {matches}/{total} expected indicators."
        elif status == "PARTIAL":
            return f"Document contains some evidence for '{control['title']}' ({matches}/{total} indicators), but coverage is incomplete."
        elif status == "FAIL":
            return f"Document lacks sufficient evidence for '{control['title']}'. Only {matches}/{total} indicators found. {control['risk_if_missing']}"
        return "Could not assess — insufficient document content."

    def calculate_score(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """Calculate transparent compliance score."""
        if not results:
            return {"score": 0, "methodology": "No controls assessed"}

        # Weight by severity
        severity_weights = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0.5}

        total_weight = 0
        passed_weight = 0
        partial_weight = 0
        failed_weight = 0

        status_counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "NOT_ASSESSED": 0}

        for result in results:
            weight = severity_weights.get(result.severity, 1)
            total_weight += weight
            status_counts[result.status] += 1

            if result.status == "PASS":
                passed_weight += weight
            elif result.status == "PARTIAL":
                partial_weight += weight * 0.5
            elif result.status == "FAIL":
                failed_weight += weight

        # Score: weighted passed / weighted total * 100
        assessed_weight = passed_weight + partial_weight + failed_weight
        score = (passed_weight + partial_weight) / assessed_weight * 100 if assessed_weight > 0 else 0

        return {
            "score": round(score, 1),
            "total_controls": len(results),
            "passed": status_counts["PASS"],
            "partial": status_counts["PARTIAL"],
            "failed": status_counts["FAIL"],
            "not_assessed": status_counts["NOT_ASSESSED"],
            "methodology": (
                f"Score = (weighted passed + 0.5×weighted partial) / weighted assessed × 100. "
                f"Weights: CRITICAL=3, HIGH=2, MEDIUM=1, LOW=0.5. "
                f"NOT_ASSESSED controls are excluded from denominator."
            ),
            "breakdown": {
                "passed_weight": round(passed_weight, 2),
                "partial_weight": round(partial_weight, 2),
                "failed_weight": round(failed_weight, 2),
                "total_weight": round(total_weight, 2),
            }
        }

compliance_service = ComplianceService()
