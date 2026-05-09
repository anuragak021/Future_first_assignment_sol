# graph — LangGraph state machine encoding the multi-agent pipeline
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestration.state import AgentState
from app.agents.supervisor import runSupervisor
from app.agents.sql_agent import runSqlAgent
from app.agents.rag_agent import runRagAgent
from app.agents.analytics_agent import runAnalyticsAgent
from app.agents.synthesizer import runSynthesizer
from app.agents.verifier import runVerifier
from app.tools.sql_tools import SqlToolRegistry
from app.config import getYamlConfig

logger = logging.getLogger(__name__)


def _routeAfterVerifier(state: AgentState) -> Literal["synthesizer", "end"]:
    # No retry loop — always proceed to finalize; verifier result is attached as disclosure
    return "end"


def _finalizeAnswer(state: AgentState) -> dict:
    if state.draftAnswer:
        draft = state.draftAnswer
        # Only add disclosure if faithfulness is genuinely low (< 0.5) and verdict is HARD_FAIL
        if (state.verifierResult
                and state.verifierResult.verdict == "HARD_FAIL"
                and state.verifierResult.faithfulnessScore < 0.5):
            from app.orchestration.state import DraftAnswer
            disclosure = (
                "\n\n---\n**Note:** Some claims could not be verified against the source data."
            )
            draft = DraftAnswer(
                answerMd=draft.answerMd + disclosure,
                claims=draft.claims,
                chartRefs=draft.chartRefs,
                uncertaintyNotes="Low faithfulness score from verifier.",
            )
        return {"finalAnswer": draft, "retryCount": state.retryCount + 1}
    return {"finalAnswer": state.draftAnswer, "retryCount": state.retryCount + 1}


def buildGraph(session: AsyncSession):
    sqlRegistry = SqlToolRegistry(session)

    async def supervisorNode(state: AgentState) -> dict:
        return runSupervisor(state)

    async def sqlNode(state: AgentState) -> dict:
        return await runSqlAgent(state, sqlRegistry)

    async def ragNode(state: AgentState) -> dict:
        return runRagAgent(state)

    async def analyticsNode(state: AgentState) -> dict:
        return runAnalyticsAgent(state)

    async def synthesizerNode(state: AgentState) -> dict:
        return runSynthesizer(state)

    async def verifierNode(state: AgentState) -> dict:
        return runVerifier(state)

    async def finalizeNode(state: AgentState) -> dict:
        return _finalizeAnswer(state)

    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisorNode)
    builder.add_node("sql", sqlNode)
    builder.add_node("rag", ragNode)
    builder.add_node("analytics", analyticsNode)
    builder.add_node("synthesizer", synthesizerNode)
    builder.add_node("verifier", verifierNode)
    builder.add_node("finalize", finalizeNode)

    # Sequential pipeline: supervisor → sql → rag → analytics → synthesizer → verifier → finalize
    # Sequential avoids fan-in double-firing (two edges → synthesizer caused it to run twice)
    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "sql")
    builder.add_edge("sql", "rag")
    builder.add_edge("rag", "analytics")
    builder.add_edge("analytics", "synthesizer")
    builder.add_edge("synthesizer", "verifier")
    builder.add_conditional_edges(
        "verifier",
        _routeAfterVerifier,
        {"synthesizer": "synthesizer", "end": "finalize"},
    )
    builder.add_edge("finalize", END)

    return builder.compile()


async def runPipeline(query: str, sessionId: str, history: list[dict], session: AsyncSession) -> AgentState:
    graph = buildGraph(session)
    initialState = AgentState(query=query, sessionId=sessionId, history=history)
    finalState = await graph.ainvoke(initialState)
    return AgentState(**finalState)
