"""Deterministic risk scoring engine."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..core.logging import logger

@dataclass
class RiskFactor:
    name: str
    weight: float
    score: float
    description: str

class RiskEngine:
    """
    Deterministic risk engine using weighted factors.
    Never allows LLM alone to determine severity.
    """

    # Risk factor definitions with weights
    FACTORS = {
        "sensitive_data": {
            "weight": 25,
            "description": "Presence of sensitive personal data categories",
        },
        "external_sharing": {
            "weight": 20,
            "description": "Data shared with external processors or third parties",
        },
        "retention_gap": {
            "weight": 15,
            "description": "Missing or excessive retention periods",
        },
        "security_gap": {
            "weight": 15,
            "description": "Inadequate security controls documented",
        },
        "evidence_gap": {
            "weight": 10,
            "description": "Missing compliance evidence",
        },
        "cross_border": {
            "weight": 10,
            "description": "Cross-border data transfers without adequate safeguards",
        },
        "volume_exposure": {
            "weight": 5,
            "description": "Large volume of data subjects increases impact",
        },
    }

    # Severity thresholds (configurable)
    THRESHOLDS = {
        "CRITICAL": (75, 100),
        "HIGH": (50, 74),
        "MEDIUM": (25, 49),
        "LOW": (0, 24),
    }

    def calculate_risk(
        self,
        pii_results: Dict[str, Any],
        compliance_results: List[Any],
        text: str,
    ) -> Dict[str, Any]:
        """
        Calculate risk score based on deterministic factors.
        """
        factors = []
        total_score = 0

        # Factor 1: Sensitive data presence
        sensitive_categories = pii_results.get("categories", {})
        sensitive_count = sum(1 for cat in ["Government ID", "Financial", "Health"] if cat in sensitive_categories)
        sensitive_score = min(sensitive_count / 3 * 25, 25)
        factors.append(RiskFactor(
            name="sensitive_data",
            weight=25,
            score=round(sensitive_score, 1),
            description=f"Detected {sensitive_count} sensitive data categories (Gov ID, Financial, Health)",
        ))
        total_score += sensitive_score

        # Factor 2: External sharing
        external_indicators = ["third party", "vendor", "processor", "external", "outsourced", "cloud"]
        external_matches = sum(1 for ind in external_indicators if ind in text.lower())
        external_score = min(external_matches / 3 * 20, 20)
        factors.append(RiskFactor(
            name="external_sharing",
            weight=20,
            score=round(external_score, 1),
            description=f"Found {external_matches} references to external sharing",
        ))
        total_score += external_score

        # Factor 3: Retention gap
        retention_keywords = ["retention", "retain", "delete", "deletion", "erase", "storage period"]
        retention_matches = sum(1 for kw in retention_keywords if kw in text.lower())
        retention_score = 15 - min(retention_matches / 3 * 15, 15)  # Inverse: fewer mentions = higher risk
        factors.append(RiskFactor(
            name="retention_gap",
            weight=15,
            score=round(retention_score, 1),
            description="Limited retention/deletion documentation found" if retention_score > 7 else "Retention controls appear documented",
        ))
        total_score += retention_score

        # Factor 4: Security gap
        security_keywords = ["encryption", "access control", "secure", "protect", "authenticate", " MFA ", "2FA"]
        security_matches = sum(1 for kw in security_keywords if kw in text.lower())
        security_score = 15 - min(security_matches / 3 * 15, 15)
        factors.append(RiskFactor(
            name="security_gap",
            weight=15,
            score=round(security_score, 1),
            description="Security controls insufficiently documented" if security_score > 7 else "Security controls appear documented",
        ))
        total_score += security_score

        # Factor 5: Evidence gap (from compliance failures)
        fail_count = sum(1 for r in compliance_results if r.status == "FAIL")
        partial_count = sum(1 for r in compliance_results if r.status == "PARTIAL")
        evidence_score = min((fail_count * 3 + partial_count * 1.5) / 10 * 10, 10)
        factors.append(RiskFactor(
            name="evidence_gap",
            weight=10,
            score=round(evidence_score, 1),
            description=f"{fail_count} controls failed, {partial_count} partial — evidence gaps detected",
        ))
        total_score += evidence_score

        # Factor 6: Cross-border
        cross_border_indicators = ["cross border", "international", "overseas", "foreign", "global"]
        cb_matches = sum(1 for ind in cross_border_indicators if ind in text.lower())
        cb_score = min(cb_matches / 2 * 10, 10)
        factors.append(RiskFactor(
            name="cross_border",
            weight=10,
            score=round(cb_score, 1),
            description=f"{cb_matches} references to cross-border transfers found",
        ))
        total_score += cb_score

        # Factor 7: Volume exposure (estimated from text length as proxy)
        volume_score = 2.5 if len(text) > 50000 else 1.5 if len(text) > 10000 else 0.5
        factors.append(RiskFactor(
            name="volume_exposure",
            weight=5,
            score=round(volume_score, 1),
            description="Document size suggests significant data processing scope" if volume_score > 1 else "Limited document scope",
        ))
        total_score += volume_score

        # Normalize to 0-100
        normalized_score = min(round(total_score, 1), 100)
        severity = self._get_severity(normalized_score)

        return {
            "risk_score": normalized_score,
            "severity": severity,
            "factors": [
                {
                    "name": f.name,
                    "weight": f.weight,
                    "score": f.score,
                    "description": f.description,
                }
                for f in factors
            ],
            "explanation": self._generate_explanation(normalized_score, severity, factors),
        }

    def _get_severity(self, score: float) -> str:
        """Map score to severity category."""
        for severity, (low, high) in self.THRESHOLDS.items():
            if low <= score <= high:
                return severity
        return "LOW"

    def _generate_explanation(self, score: float, severity: str, factors: List[RiskFactor]) -> str:
        """Generate human-readable risk explanation."""
        top_factors = sorted(factors, key=lambda x: x.score, reverse=True)[:3]
        factor_text = "; ".join([f"{f.name}: {f.score}/{f.weight}" for f in top_factors])

        return (
            f"{severity} risk (score {score}/100) because: {factor_text}. "
            f"Primary drivers: {', '.join([f.name for f in top_factors])}."
        )

    def get_risk_distribution(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by severity."""
        dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in findings:
            sev = finding.get("severity", "LOW")
            if sev in dist:
                dist[sev] += 1
        return dist

risk_engine = RiskEngine()
