# chat — POST /chat: runs the full agent pipeline and returns the answer
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import getDbSession
from app.orchestration.graph import runPipeline
from app.observability.trace_store import getTraceStore

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    sessionId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: list[dict] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    sessionId: str
    answerMd: str
    chartSpecs: list[dict]
    toolTrace: list[dict]
    verdict: str
    faithfulnessScore: float
    uncertaintyNotes: str | None


import hashlib

# Simple in-memory API cache
_api_cache: dict[str, ChatResponse] = {}

def _get_cache_key(query: str, filters: dict) -> str:
    key_str = f"{query.strip().lower()}|{sorted(filters.items())}"
    return hashlib.md5(key_str.encode()).hexdigest()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(getDbSession),
) -> ChatResponse:
    logger.info(f"Chat request session={request.sessionId} query_len={len(request.query)}")

    # 1. API-Level Caching (Only cache if there is no conversation history)
    cache_key = None
    if not request.history:
        cache_key = _get_cache_key(request.query, request.filters)
        if cache_key in _api_cache:
            logger.info("Cache hit! Returning instant response.")
            cached_resp = _api_cache[cache_key]
            # Give it the new session ID so the frontend doesn't get confused
            cached_resp.sessionId = request.sessionId
            return cached_resp

    try:
        finalState = await runPipeline(
            query=request.query,
            sessionId=request.sessionId,
            history=request.history,
            session=session,
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return ChatResponse(
            sessionId=request.sessionId,
            answerMd="I'm sorry, but I couldn't process that request. The system may have blocked the query for safety reasons, or there was an internal issue. Please try asking in a different way.",
            chartSpecs=[],
            toolTrace=[],
            verdict="UNKNOWN",
            faithfulnessScore=0.0,
            uncertaintyNotes="System error or blocked request."
        )

    answer = finalState.finalAnswer
    if not answer:
        return ChatResponse(
            sessionId=request.sessionId,
            answerMd="I'm sorry, I couldn't generate an answer based on the available data.",
            chartSpecs=[],
            toolTrace=[],
            verdict="UNKNOWN",
            faithfulnessScore=0.0,
            uncertaintyNotes="No answer generated."
        )

    verdict = "UNKNOWN"
    faithfulness = 1.0
    if finalState.verifierResult:
        verdict = finalState.verifierResult.verdict
        faithfulness = finalState.verifierResult.faithfulnessScore

    chartSpecs = []
    if finalState.analyticsEvidence:
        chartSpecs = finalState.analyticsEvidence.chartSpecs

    traceStore = getTraceStore()
    traceStore.saveTrace(
        sessionId=request.sessionId,
        query=request.query,
        toolTrace=finalState.toolTrace,
        verdict=verdict,
        faithfulness=faithfulness,
    )

    response = ChatResponse(
        sessionId=request.sessionId,
        answerMd=answer.answerMd,
        chartSpecs=chartSpecs,
        toolTrace=finalState.toolTrace,
        verdict=verdict,
        faithfulnessScore=faithfulness,
        uncertaintyNotes=answer.uncertaintyNotes,
    )
    
    if cache_key:
        _api_cache[cache_key] = response
        
    return response
