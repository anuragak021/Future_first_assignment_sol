# state — shared LangGraph state and typed contracts between agents
from __future__ import annotations
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field
import operator


# ── Supervisor contract ──────────────────────────────────────────────────────

class EvidenceRequirement(BaseModel):
    agent: Literal["sql", "rag", "analytics"]
    purpose: str
    mustReturn: list[str] = Field(default_factory=list)
    minRows: int = 1


class ExpectedAnswerShape(BaseModel):
    mustCite: bool = True
    mustIncludeNumbers: bool = False
    mustIncludeChart: bool = False
    claimTypes: list[Literal["ranking", "trend", "comparison", "causal", "recommendation"]] = Field(default_factory=list)


class Plan(BaseModel):
    intent: Literal["fact_lookup", "trend", "comparison", "diagnosis", "recommendation", "doc_qa"]
    evidenceRequirements: list[EvidenceRequirement] = Field(default_factory=list)
    expectedShape: ExpectedAnswerShape = Field(default_factory=ExpectedAnswerShape)
    parallel: bool = True
    rationale: str = ""


# ── Worker outputs ───────────────────────────────────────────────────────────

class SqlEvidence(BaseModel):
    rows: list[dict] = Field(default_factory=list)
    toolName: str = ""
    params: dict = Field(default_factory=dict)


class RagChunk(BaseModel):
    text: str
    sourceDoc: str
    page: int = 0
    section: str = ""
    score: float = 0.0
    trust: Literal["trusted", "noise"] = "trusted"


class RagEvidence(BaseModel):
    chunks: list[RagChunk] = Field(default_factory=list)


class AnalyticsEvidence(BaseModel):
    kpis: dict = Field(default_factory=dict)
    chartSpecs: list[dict] = Field(default_factory=list)
    summary: str = ""


# ── Synthesizer / Verifier ───────────────────────────────────────────────────

class Claim(BaseModel):
    text: str
    citations: list[str] = Field(default_factory=list)
    entailmentScore: float = 1.0
    claimType: str = "fact"


class DraftAnswer(BaseModel):
    answerMd: str
    claims: list[Claim] = Field(default_factory=list)
    chartRefs: list[str] = Field(default_factory=list)
    uncertaintyNotes: Optional[str] = None


class VerifierResult(BaseModel):
    passed: bool
    verdict: Literal["PASS", "SOFT_FAIL", "HARD_FAIL"]
    failedChecks: list[str] = Field(default_factory=list)
    feedback: str = ""
    faithfulnessScore: float = 1.0


# ── LangGraph state ──────────────────────────────────────────────────────────

class AgentState(BaseModel):
    query: str = ""
    sessionId: str = ""
    history: list[dict] = Field(default_factory=list)

    plan: Optional[Plan] = None

    sqlEvidence: Optional[SqlEvidence] = None
    ragEvidence: Optional[RagEvidence] = None
    analyticsEvidence: Optional[AnalyticsEvidence] = None

    draftAnswer: Optional[DraftAnswer] = None
    verifierResult: Optional[VerifierResult] = None

    retryCount: int = 0
    finalAnswer: Optional[DraftAnswer] = None

    # Annotated so parallel agents can each append without conflict
    toolTrace: Annotated[list[dict], operator.add] = Field(default_factory=list)
    errors: Annotated[list[str], operator.add] = Field(default_factory=list)
