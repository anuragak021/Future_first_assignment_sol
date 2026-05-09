# ingestion — PDF → chunks → ChromaDB vector store
import logging
from pathlib import Path
from typing import Optional
import pdfplumber
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import getSettings, getYamlConfig
from app.llm.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

PDF_DIR = Path(__file__).parent.parent.parent.parent / "data" / "pdfs"


class DocumentIngestionService:
    """Handles PDF ingestion: extract → chunk → embed → store in Chroma."""

    def __init__(self) -> None:
        settings = getSettings()
        yamlCfg = getYamlConfig()
        self._chunkSize: int = yamlCfg.get("retrieval", {}).get("chunk_size", 512)
        self._chunkOverlap: int = yamlCfg.get("retrieval", {}).get("chunk_overlap", 64)
        if settings.use_embedded_chroma:
            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        self._collection = self._client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )
        self._embedder = EmbeddingService()

    def _extractPages(self, pdfPath: Path) -> list[dict]:
        pages = []
        with pdfplumber.open(pdfPath) as pdf:
            for pageNum, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append({
                        "text": text,
                        "page": pageNum,
                        "source_doc": pdfPath.name,
                        "section": None,
                    })
        return pages

    def _chunkText(self, text: str) -> list[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + self._chunkSize
            chunks.append(" ".join(words[start:end]))
            start += self._chunkSize - self._chunkOverlap
        return [c for c in chunks if len(c.strip()) > 20]

    def ingestPdf(self, pdfPath: Path, trust: str = "trusted") -> int:
        pages = self._extractPages(pdfPath)
        docs, metadatas, ids = [], [], []
        chunkIdx = 0
        for pageData in pages:
            for chunk in self._chunkText(pageData["text"]):
                chunkId = f"{pdfPath.stem}_p{pageData['page']}_c{chunkIdx}"
                docs.append(chunk)
                metadatas.append({
                    "source_doc": pageData["source_doc"],
                    "page": pageData["page"],
                    "trust": trust,
                    "section": pageData["section"] or "",
                })
                ids.append(chunkId)
                chunkIdx += 1

        if not docs:
            return 0

        embeddings = self._embedder.encode(docs)
        self._collection.upsert(
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Ingested {len(docs)} chunks from {pdfPath.name}")
        return len(docs)

    def ingestAllPdfs(self) -> dict[str, int]:
        results = {}
        for pdfPath in PDF_DIR.glob("*.pdf"):
            count = self.ingestPdf(pdfPath)
            results[pdfPath.name] = count
        return results

    def queryDocuments(
        self,
        queryText: str,
        topK: int = 4,
        trustFilter: Optional[str] = None,
    ) -> list[dict]:
        queryEmbedding = self._embedder.encode([queryText])[0]
        where = {"trust": trustFilter} if trustFilter else None
        results = self._collection.query(
            query_embeddings=[queryEmbedding],
            n_results=topK,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text": doc,
                "source_doc": meta.get("source_doc", ""),
                "page": meta.get("page", 0),
                "section": meta.get("section", ""),
                "score": float(1 - dist),
                "trust": meta.get("trust", "trusted"),
            })
        return chunks
