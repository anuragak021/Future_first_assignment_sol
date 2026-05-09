# ragAgent — retrieves and reranks document chunks relevant to the query
import logging
from app.orchestration.state import AgentState, RagEvidence, RagChunk
from app.tools.vector_tools import VectorSearchTool
from app.config import getYamlConfig

logger = logging.getLogger(__name__)


def runRagAgent(state: AgentState) -> dict:
    if not state.plan:
        return {"ragEvidence": RagEvidence()}

    needsRag = any(r.agent == "rag" for r in state.plan.evidenceRequirements)
    if not needsRag:
        return {"ragEvidence": RagEvidence()}

    yamlCfg = getYamlConfig()
    noiseChunks: int = yamlCfg.get("eval", {}).get("noise_chunks", 0)
    topK: int = yamlCfg.get("retrieval", {}).get("top_k", 4)

    tool = VectorSearchTool()
    try:
        if noiseChunks > 0:
            rawChunks = tool.searchWithNoise(state.query, noiseChunks=noiseChunks, topK=topK)
        else:
            rawChunks = tool.search(state.query, topK=topK)
    except Exception as e:
        logger.error(f"RAG agent vector search failed: {e}")
        rawChunks = []

    chunks = [
        RagChunk(
            text=c["text"],
            sourceDoc=c.get("source_doc", ""),
            page=c.get("page", 0),
            section=c.get("section", ""),
            score=c.get("score", 0.0),
            trust=c.get("trust", "trusted"),
        )
        for c in rawChunks
    ]

    trace = {"agent": "rag_agent", "chunksRetrieved": len(chunks), "query": state.query}
    return {"ragEvidence": RagEvidence(chunks=chunks), "toolTrace": [trace]}
