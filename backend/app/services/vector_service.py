"""ChromaDB vector storage for RAG."""
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.config import settings
from ..core.logging import logger

class VectorService:
    """ChromaDB-based vector storage with organization isolation."""

    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIRECTORY
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None

    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=str(self.persist_dir))
                self._collection = self._client.get_or_create_collection(
                    name="privacy_documents",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB client initialized")
            except ImportError:
                logger.warning("ChromaDB not available — RAG disabled")
                return None
            except Exception as e:
                logger.error(f"ChromaDB init failed: {e}")
                return None
        return self._client

    def is_available(self) -> bool:
        return self._get_client() is not None

    def add_document_chunks(
        self,
        document_id: int,
        organization_id: int,
        filename: str,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> bool:
        """Split document into chunks and store vectors."""
        if not self.is_available():
            logger.warning("ChromaDB not available — skipping vector storage")
            return False

        try:
            chunks = self._chunk_text(text, chunk_size, chunk_overlap)

            ids = []
            documents = []
            metadatas = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{organization_id}_{document_id}_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "document_id": document_id,
                    "organization_id": organization_id,
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_id": chunk_id,
                })

            self._collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

            logger.info(f"Stored {len(chunks)} chunks for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Vector storage failed: {e}")
            return False

    def query(
        self,
        organization_id: int,
        query_text: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query vectors for relevant chunks, filtered by organization."""
        if not self.is_available():
            return []

        try:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"organization_id": organization_id},
            )

            chunks = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    chunks.append({
                        "text": doc,
                        "metadata": metadata,
                        "distance": distance,
                    })

            return chunks
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return []

    def delete_document(self, document_id: int, organization_id: int) -> bool:
        """Delete all chunks for a document."""
        if not self.is_available():
            return False

        try:
            self._collection.delete(
                where={
                    "document_id": document_id,
                    "organization_id": organization_id,
                }
            )
            return True
        except Exception as e:
            logger.error(f"Vector deletion failed: {e}")
            return False

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, newline, or space near boundary
                for i in range(min(end + 100, len(text)) - 1, end - 100, -1):
                    if i < len(text) and text[i] in ".\n ":
                        end = i + 1
                        break

            chunks.append(text[start:end].strip())
            start = end - chunk_overlap

        return chunks

vector_service = VectorService()
