# RerankerService — cross-encoder reranking of retrieved chunks
import logging
from functools import lru_cache
from sentence_transformers import CrossEncoder
from app.config import getYamlConfig

logger = logging.getLogger(__name__)


class RerankerService:
    """Uses a cross-encoder to reorder retrieved chunks by relevance to the query."""

    def __init__(self) -> None:
        yamlCfg = getYamlConfig()
        modelName: str = yamlCfg.get("reranker", {}).get("model", "BAAI/bge-reranker-base")
        device: str = yamlCfg.get("reranker", {}).get("device", "cpu")
        logger.info(f"Loading reranker model: {modelName}")
        self._model = CrossEncoder(modelName, device=device)

    def rerank(self, query: str, chunks: list[dict], topK: int = 4) -> list[dict]:
        if not chunks:
            return []
        pairs = [(query, c["text"]) for c in chunks]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
        reranked = []
        for score, chunk in ranked[:topK]:
            chunk = dict(chunk)
            chunk["score"] = float(score)
            reranked.append(chunk)
        return reranked


@lru_cache()
def getRerankerService() -> RerankerService:
    return RerankerService()
