"""Personal data detection engine using regex, keywords, and contextual analysis."""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

from ..core.logging import logger
from ..utils.validators import mask_email, mask_phone, mask_aadhaar, mask_pan, mask_generic

@dataclass
class PIIDetection:
    type: str
    value_masked: str
    confidence: float
    source: str
    context: str
    position: Optional[int] = None

class PIIDetectionService:
    """Multi-layer PII detection: regex + keywords + contextual analysis."""

    # Detection patterns with confidence weights
    PATTERNS = {
        "EMAIL": {
            "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "confidence": 0.97,
            "context_keywords": ["email", "e-mail", "contact", "mail"],
        },
        "PHONE": {
            "regex": r"(?:\+91[-\s]?)?[6-9]\d{9}|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "confidence": 0.92,
            "context_keywords": ["phone", "mobile", "contact", "tel", "call"],
        },
        "AADHAAR": {
            "regex": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "confidence": 0.85,
            "context_keywords": ["aadhaar", "uid", "uidai", "identity"],
            "validator": lambda x: len(re.sub(r"\D", "", x)) == 12,
        },
        "PAN": {
            "regex": r"\b[A-Z]{5}\d{4}[A-Z]\b",
            "confidence": 0.90,
            "context_keywords": ["pan", "permanent account", "tax", "income"],
        },
        "PASSPORT": {
            "regex": r"\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b",
            "confidence": 0.80,
            "context_keywords": ["passport", "travel", "visa"],
        },
        "BANK_ACCOUNT": {
            "regex": r"\b\d{9,18}\b",
            "confidence": 0.70,
            "context_keywords": ["account", "bank", "ifsc", "account number", "banking"],
        },
        "IFSC": {
            "regex": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
            "confidence": 0.95,
            "context_keywords": ["ifsc", "bank", "branch", "transfer"],
        },
        "CREDIT_CARD": {
            "regex": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "confidence": 0.88,
            "context_keywords": ["card", "credit", "debit", "payment", "visa", "mastercard"],
            "validator": lambda x: len(re.sub(r"\D", "", x)) in [15, 16],
        },
        "IP_ADDRESS": {
            "regex": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "confidence": 0.85,
            "context_keywords": ["ip", "address", "network", "server"],
        },
        "PIN_CODE": {
            "regex": r"\b\d{6}\b",
            "confidence": 0.75,
            "context_keywords": ["pin", "zip", "postal", "code", "address"],
            "validator": lambda x: x.startswith(("1", "2", "3", "4", "5", "6", "7", "8")),
        },
        "EMPLOYEE_ID": {
            "regex": r"\b(?:EMP|EMPID|ID)[-\s]?\d{3,6}\b",
            "confidence": 0.80,
            "context_keywords": ["employee", "staff", "id", "empid", "personnel"],
        },
        "DATE_OF_BIRTH": {
            "regex": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            "confidence": 0.65,
            "context_keywords": ["dob", "birth", "born", "date of birth", "age"],
        },
    }

    # Category mapping
    CATEGORY_MAP = {
        "EMAIL": "Contact",
        "PHONE": "Contact",
        "AADHAAR": "Government ID",
        "PAN": "Government ID",
        "PASSPORT": "Government ID",
        "BANK_ACCOUNT": "Financial",
        "IFSC": "Financial",
        "CREDIT_CARD": "Financial",
        "IP_ADDRESS": "Online Identifier",
        "PIN_CODE": "Location",
        "EMPLOYEE_ID": "Employment",
        "DATE_OF_BIRTH": "Identity",
    }

    def detect(self, text: str, document_id: int = None) -> Dict[str, Any]:
        """
        Detect PII in text.
        Returns structured detection results with masked values.
        """
        if not text or len(text.strip()) < 10:
            return {"detections": [], "categories": {}, "summary": "No text to analyze"}

        detections: List[PIIDetection] = []
        category_counts = defaultdict(int)

        # Normalize text for analysis
        normalized_text = text.lower()

        for pii_type, config in self.PATTERNS.items():
            matches = list(re.finditer(config["regex"], text, re.IGNORECASE))

            for match in matches:
                value = match.group()

                # Run validator if present
                if "validator" in config and not config["validator"](value):
                    continue

                # Contextual confidence boost
                context_window = self._get_context(text, match.start(), match.end())
                context_confidence = self._check_context(context_window, config.get("context_keywords", []))

                final_confidence = min(config["confidence"] + context_confidence * 0.1, 1.0)

                # Mask the value
                masked = self._mask_value(pii_type, value)

                detection = PIIDetection(
                    type=pii_type,
                    value_masked=masked,
                    confidence=round(final_confidence, 2),
                    source="regex+context",
                    context=context_window[:200],
                    position=match.start(),
                )
                detections.append(detection)
                category_counts[self.CATEGORY_MAP.get(pii_type, "Other")] += 1

        # spaCy NER enhancement (if available)
        spacy_detections = self._spacy_detect(text)
        detections.extend(spacy_detections)
        for d in spacy_detections:
            category_counts[self.CATEGORY_MAP.get(d.type, "Other")] += 1

        # Deduplicate by position
        detections = self._deduplicate(detections)

        # Sort by confidence
        detections.sort(key=lambda x: x.confidence, reverse=True)

        return {
            "detections": [self._detection_to_dict(d) for d in detections],
            "categories": dict(category_counts),
            "summary": f"Detected {len(detections)} potential data elements across {len(category_counts)} categories",
        }

    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Extract context window around a match."""
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        return text[ctx_start:ctx_end].strip()

    def _check_context(self, context: str, keywords: List[str]) -> float:
        """Check if context contains relevant keywords."""
        context_lower = context.lower()
        matches = sum(1 for kw in keywords if kw in context_lower)
        return min(matches / max(len(keywords), 1), 1.0)

    def _mask_value(self, pii_type: str, value: str) -> str:
        """Mask a detected value based on type."""
        maskers = {
            "EMAIL": mask_email,
            "PHONE": mask_phone,
            "AADHAAR": mask_aadhaar,
            "PAN": mask_pan,
        }
        if pii_type in maskers:
            return maskers[pii_type](value)
        return mask_generic(value)

    def _spacy_detect(self, text: str) -> List[PIIDetection]:
        """Enhance detection with spaCy NER."""
        detections = []
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:100000])  # Limit for performance

            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE"]:
                    pii_type = "NAME" if ent.label_ == "PERSON" else "ORGANIZATION" if ent.label_ == "ORG" else "LOCATION"
                    detections.append(PIIDetection(
                        type=pii_type,
                        value_masked=mask_generic(ent.text, 3),
                        confidence=0.75,
                        source="spacy-ner",
                        context=text[max(0, ent.start_char-50):ent.end_char+50],
                        position=ent.start_char,
                    ))
        except Exception as e:
            logger.debug(f"spaCy NER not available or failed: {e}")

        return detections

    def _deduplicate(self, detections: List[PIIDetection]) -> List[PIIDetection]:
        """Remove overlapping detections, keeping highest confidence."""
        if not detections:
            return detections

        sorted_dets = sorted(detections, key=lambda x: x.confidence, reverse=True)
        result = []
        used_positions = set()

        for det in sorted_dets:
            if det.position is None:
                result.append(det)
                continue
            # Check if position overlaps with existing (within 20 chars)
            overlap = any(abs(det.position - pos) < 20 for pos in used_positions)
            if not overlap:
                result.append(det)
                used_positions.add(det.position)

        return result

    def _detection_to_dict(self, detection: PIIDetection) -> Dict[str, Any]:
        return {
            "type": detection.type,
            "value_masked": detection.value_masked,
            "confidence": detection.confidence,
            "source": detection.source,
            "context": detection.context,
        }

pii_detection_service = PIIDetectionService()
