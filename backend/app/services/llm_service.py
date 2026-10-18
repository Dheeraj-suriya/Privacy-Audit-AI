"""LLM provider interface with Ollama support and fallback."""
import json
import requests
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

from ..core.config import settings
from ..core.logging import logger

class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
        """Generate a completion for the provided prompt."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the provider is available."""
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.enabled = settings.OLLAMA_ENABLED

    def is_available(self) -> bool:
        if not self.enabled:
            return False

        try:
            resp = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return resp.status_code == 200

        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:

        if not self.is_available():
            raise RuntimeError("Ollama not available")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 512,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=600,
            )

            resp.raise_for_status()

            data = resp.json()

            return data.get("response", "")

        except requests.exceptions.Timeout:
            logger.error(
                "Ollama generation timed out after 600 seconds"
            )
            raise RuntimeError("AI generation timed out")

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Ollama generation request failed: {e}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Ollama generation failed: {e}"
            )
            raise

class FallbackProvider(LLMProvider):
    """Deterministic fallback when no LLM is available."""

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
        return "[AI analysis unavailable — using deterministic rule-based assessment]"

class LLMService:
    """LLM service with provider abstraction and fallback."""

    def __init__(self):
        self.ollama = OllamaProvider()
        self.fallback = FallbackProvider()
        self._check_availability()

    def _check_availability(self):
        if self.ollama.is_available():
            logger.info(f"Ollama provider ready: {settings.OLLAMA_MODEL}")
        else:
            logger.warning("Ollama not available — using fallback mode")

    @property
    def provider(self) -> LLMProvider:
        if self.ollama.is_available():
            return self.ollama
        return self.fallback

    @property
    def ai_available(self) -> bool:
        return self.ollama.is_available()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3) -> str:
        return self.provider.generate(prompt, system_prompt, temperature)

    def analyze_document(self, text: str, max_length: int = 8000) -> Dict[str, Any]:
        """Use LLM to enhance document analysis."""
        if not self.ai_available:
            return {"enhanced": False, "note": "AI enhancement unavailable"}

        # Truncate text if too long
        truncated = text[:max_length] if len(text) > max_length else text
        
        system_prompt = """You are a privacy analysis assistant. Analyze the provided document text for privacy-related content.
Respond ONLY with a JSON object in this exact format:
{
  "processing_activities": ["activity1", "activity2"],
  "data_subjects": ["customers", "employees"],
  "data_categories": ["contact", "financial"],
  "risk_indicators": ["missing retention policy", "unclear third-party sharing"],
  "summary": "Brief summary of privacy posture"
}
Do not include any other text."""

        prompt = f"""Analyze this privacy document:

{truncated}

Provide JSON analysis."""

        try:
            response = self.generate(prompt, system_prompt, temperature=0.1)
            # Extract JSON from response
            json_match = self._extract_json(response)
            if json_match:
                return {"enhanced": True, "llm_analysis": json_match}
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")

        return {"enhanced": False, "note": "AI analysis failed — using rule-based assessment"}

    def chat_response(self, question: str, context_chunks: List[str], conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate RAG-based chat response."""
        if not self.ai_available:
            return {
                "response": "I could not find sufficient evidence in the uploaded documents. (AI assistant is currently unavailable — using deterministic rules only.)",
                "sources": [],
            }

        context = "\n\n".join([f"[Document chunk {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks[:5])])

        system_prompt = """You are PrivacyAudit AI, a privacy compliance assistant. 
Rules:
- Answer ONLY using the provided document evidence
- Clearly distinguish evidence from inference
- Never invent documents, policies, or evidence
- Never claim definitive legal advice
- Explain uncertainty
- Recommend professional review for high-impact decisions
- Mask personal information
- Prefer concise, actionable responses
- If evidence is insufficient, say so explicitly"""

        history_text = ""
        if conversation_history:
            for msg in conversation_history[-4:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        prompt = f"""Document Evidence:
{context}

{history_text}
User Question: {question}

Provide a concise answer based on the evidence above. Cite specific document references. If the evidence does not contain the answer, state that clearly."""

        try:
            response = self.generate(prompt, system_prompt, temperature=0.2)

            # Extract sources
            sources = []
            for i, chunk in enumerate(context_chunks[:3]):
                sources.append({
                    "document_name": f"Document {i+1}",
                    "section": "Document Evidence",
                    "snippet": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                })

            return {
                "response": response,
                "sources": sources,
            }
        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            return {
                "response": "I encountered an error processing your question. Please try again.",
                "sources": [],
            }

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON object from text."""
        import re
        try:
            # Find JSON between braces
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            pass
        return None

llm_service = LLMService()
