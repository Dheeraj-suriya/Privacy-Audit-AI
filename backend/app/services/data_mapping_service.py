"""Data flow and processing activity mapping."""
import re
from typing import List, Dict, Any, Optional

from ..core.logging import logger

class DataMappingService:
    """Extract processing activities and data flows from documents."""

    def extract_processing_activities(self, text: str) -> List[Dict[str, Any]]:
        """Extract processing activities from text."""
        activities = []

        # Activity patterns
        activity_indicators = [
            (r"(?:collect|collection|gather|gathering).*?data", "Data Collection"),
            (r"(?:process|processing).*?data", "Data Processing"),
            (r"(?:store|storage|retain|retention).*?data", "Data Storage"),
            (r"(?:share|sharing|disclose|disclosure).*?data", "Data Sharing"),
            (r"(?:analyze|analysis|analytics).*?data", "Data Analytics"),
            (r"(?:transfer|transmission).*?data", "Data Transfer"),
            (r"(?:delete|deletion|erase|erasure).*?data", "Data Deletion"),
        ]

        text_lower = text.lower()

        for pattern, default_name in activity_indicators:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for i, match in enumerate(matches[:3]):  # Limit to 3 per type
                context = text[max(0, match.start()-100):match.end()+200]

                activity = {
                    "name": self._extract_activity_name(context) or f"{default_name} {i+1}",
                    "purpose": self._extract_purpose(context),
                    "data_subjects": self._extract_data_subjects(context),
                    "data_categories": self._extract_data_categories(context),
                    "collection_source": self._extract_source(context),
                    "storage_location": self._extract_storage(context),
                    "retention_period": self._extract_retention(context),
                    "external_processors": self._extract_processors(context),
                    "cross_border_transfer": "cross border" in text_lower or "international" in text_lower,
                    "legal_basis": self._extract_legal_basis(context),
                    "risk_level": "MEDIUM",  # Default, refined by risk engine
                    "owner": None,
                }
                activities.append(activity)

        # Deduplicate by name
        seen = set()
        unique = []
        for act in activities:
            if act["name"] not in seen:
                seen.add(act["name"])
                unique.append(act)

        return unique[:10]  # Limit to 10 activities

    def extract_data_flows(self, text: str) -> List[Dict[str, Any]]:
        """Extract data flows from text."""
        flows = []

        # Flow patterns: "X to Y", "X sends to Y", "X shares with Y"
        flow_patterns = [
            r"([A-Z][A-Za-z\s]+?)(?:\s+(?:to|sends? to|shares? with|transfers? to|provides? to))\s+([A-Z][A-Za-z\s]+?)(?:\s+(?:for|to|purpose|under))",
        ]

        for pattern in flow_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1).strip()
                dest = match.group(2).strip()

                if len(source) > 3 and len(dest) > 3 and source != dest:
                    flows.append({
                        "source": source,
                        "destination": dest,
                        "data_categories": self._extract_data_categories(text[match.start()-50:match.end()+50]),
                        "purpose": self._extract_purpose(text[match.start()-50:match.end()+100]),
                        "risk_level": "MEDIUM",
                    })

        # Also detect common system flows
        systems = self._detect_systems(text)
        if len(systems) >= 2:
            for i in range(len(systems) - 1):
                flows.append({
                    "source": systems[i],
                    "destination": systems[i + 1],
                    "data_categories": "Personal data",
                    "purpose": "Processing",
                    "risk_level": "MEDIUM",
                })

        return flows[:15]

    def _extract_activity_name(self, context: str) -> Optional[str]:
        """Try to extract a specific activity name."""
        # Look for quoted names or capitalized phrases
        match = re.search(r'"([^"]{3,50})"', context)
        if match:
            return match.group(1)
        return None

    def _extract_purpose(self, context: str) -> str:
        """Extract purpose from context."""
        purpose_patterns = [
            r"purpose[s]?\s+(?:is|are|of)\s+([^\.]{10,200})",
            r"(?:to|for)\s+([^\.]{10,200}?(?:service|provide|improve|manage|process))",
        ]
        for pattern in purpose_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        return "Not specified in document"

    def _extract_data_subjects(self, context: str) -> str:
        """Extract data subject categories."""
        subjects = []
        keywords = {
            "customer": "Customers",
            "employee": "Employees",
            "user": "Users",
            "patient": "Patients",
            "student": "Students",
            "visitor": "Visitors",
            "member": "Members",
            "applicant": "Applicants",
        }
        context_lower = context.lower()
        for kw, label in keywords.items():
            if kw in context_lower:
                subjects.append(label)
        return ", ".join(subjects) if subjects else "Not specified"

    def _extract_data_categories(self, context: str) -> str:
        """Extract data categories."""
        categories = []
        keywords = {
            "name": "Identity",
            "email": "Contact",
            "phone": "Contact",
            "address": "Location",
            "payment": "Financial",
            "health": "Health",
            "biometric": "Biometric",
            "location": "Location",
        }
        context_lower = context.lower()
        for kw, label in keywords.items():
            if kw in context_lower and label not in categories:
                categories.append(label)
        return ", ".join(categories) if categories else "Personal data"

    def _extract_source(self, context: str) -> str:
        """Extract collection source."""
        if "website" in context.lower():
            return "Website"
        if "app" in context.lower() or "application" in context.lower():
            return "Application"
        if "form" in context.lower():
            return "Forms"
        return "Not specified"

    def _extract_storage(self, context: str) -> str:
        """Extract storage location."""
        if "cloud" in context.lower():
            return "Cloud"
        if "database" in context.lower() or "db" in context.lower():
            return "Database"
        if "server" in context.lower():
            return "Server"
        return "Not specified"

    def _extract_retention(self, context: str) -> str:
        """Extract retention period."""
        match = re.search(r"(\d+)\s*(day|month|year|week)", context, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {match.group(2)}s"
        return "Not specified"

    def _extract_processors(self, context: str) -> str:
        """Extract external processors."""
        processors = []
        if "third party" in context.lower():
            processors.append("Third-party processors")
        if "vendor" in context.lower():
            processors.append("Vendors")
        return ", ".join(processors) if processors else "None identified"

    def _extract_legal_basis(self, context: str) -> str:
        """Extract legal basis."""
        bases = []
        if "consent" in context.lower():
            bases.append("Consent")
        if "contract" in context.lower():
            bases.append("Contract")
        if "legal obligation" in context.lower():
            bases.append("Legal Obligation")
        if "legitimate interest" in context.lower():
            bases.append("Legitimate Interest")
        return ", ".join(bases) if bases else "Not specified"

    def _detect_systems(self, text: str) -> List[str]:
        """Detect system names in text."""
        systems = []
        system_keywords = [
            "website", "application", "server", "database", "CRM", "ERP",
            "payment gateway", "analytics", "cloud", "API", "mobile app",
            "data warehouse", "third party", "vendor", "processor"
        ]
        text_lower = text.lower()
        for kw in system_keywords:
            if kw in text_lower:
                systems.append(kw.title())
        return list(dict.fromkeys(systems))  # Remove duplicates while preserving order

data_mapping_service = DataMappingService()
