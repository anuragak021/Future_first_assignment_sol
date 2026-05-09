# vectorTools — typed interface for document retrieval via ChromaDB similarity search
import logging
from typing import Optional
from app.data.ingestion import DocumentIngestionService
from app.config import getYamlConfig

logger = logging.getLogger(__name__)


class VectorSearchTool:
    """Retrieves relevant document chunks using ChromaDB similarity (no cross-encoder reranker)."""

    def __init__(self) -> None:
        yamlCfg = getYamlConfig()
        self._topK: int = yamlCfg.get("retrieval", {}).get("top_k", 4)
        self._ingestionSvc = DocumentIngestionService()

    def search(
        self,
        query: str,
        topK: Optional[int] = None,
        trustFilter: Optional[str] = None,
    ) -> list[dict]:
        k = topK or self._topK
        return self._ingestionSvc.queryDocuments(
            queryText=query,
            topK=k,
            trustFilter=trustFilter,
        )

    def searchWithNoise(
        self,
        query: str,
        noiseChunks: int = 2,
        topK: Optional[int] = None,
    ) -> list[dict]:
        trusted = self.search(query, topK=topK, trustFilter="trusted")
        noise = self.search(query, topK=noiseChunks, trustFilter="noise")
        return (trusted + noise)[: (topK or self._topK) + noiseChunks]
