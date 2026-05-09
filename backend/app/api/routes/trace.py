# trace — GET /trace/{sessionId}: returns tool trace history for the frontend audit pane
from fastapi import APIRouter
from app.observability.trace_store import getTraceStore

router = APIRouter()


@router.get("/trace/{sessionId}")
async def getTrace(sessionId: str, limit: int = 20) -> list[dict]:
    store = getTraceStore()
    return store.getTracesForSession(sessionId=sessionId, limit=limit)
