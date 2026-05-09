# EmbeddingService — local BGE-small embeddings, singleton
import logging
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.config import getYamlConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Wraps a local sentence-transformers model for document and query embedding."""

    def __init__(self) -> None:
        yamlCfg = getYamlConfig()
        modelName: str = yamlCfg.get("embedding", {}).get("model", "BAAI/bge-small-en-v1.5")
        device: str = yamlCfg.get("embedding", {}).get("device", "cpu")
        logger.info(f"Loading embedding model: {modelName}")
        self._model = SentenceTransformer(modelName, device=device)

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()


@lru_cache()
def getEmbeddingService() -> EmbeddingService:
    return EmbeddingService()
