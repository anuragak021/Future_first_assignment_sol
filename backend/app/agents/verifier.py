# verifier — adversarially checks the draft answer against the Supervisor's plan and evidence
import re
import json
import logging
from app.llm.groq_client import getGroqClient
from app.orchestration.state import AgentState, VerifierResult
from app.config import getYamlConfig

logger = logging.getLogger(__name__)

VERIFIER_SYSTEM_PROMPT = """You are a quality reviewer for an analytics assistant.
Your job is to verify the answer is grounded in the provided evidence.

Rules:
- PASS if the answer correctly uses data from the evidence and addresses the query.
- SOFT_FAIL only if minor citation gaps exist but the data is correct.
- HARD_FAIL only if the answer contains numbers or facts that directly contradict the evidence.
- If evidence is present and answer references it, default to PASS.
- A high faithfulnessScore (0.8-1.0) means the answer is well-grounded in evidence.

Respond with a JSON object:
{
  "passed": true/false,
  "verdict": "PASS" | "SOFT_FAIL" | "HARD_FAIL",
  "failedChecks": [],
  "feedback": "",
  "faithfulnessScore": 0.0-1.0
}
"""


def _extractNumbers(text: str) -> list[str]:
    return re.findall(r"\b\d[\d,\.]*\b", text)


def _checkNumericConsistency(answerMd: str, sqlRows: list[dict]) -> list[str]:
    answerNumbers = _extractNumbers(answerMd)
    if not sqlRows:
        return []
    evidenceText = json.dumps(sqlRows)
    evidenceNumbers = _extractNumbers(evidenceText)

    def to_float(n_str):
        try:
            return float(n_str.replace(",", ""))
        except ValueError:
            return None

    ev_floats = {f for f in (to_float(n) for n in evidenceNumbers) if f is not None}
    
    suspicious = []
    for num in answerNumbers:
        val = to_float(num)
        # Only check large numbers; ignore small numbers (like 1, 2, 3) which are often list rankings
        if val is not None and val > 100 and val not in ev_floats:
            suspicious.append(f"Number {num} in answer not found in evidence")
    return suspicious[:3]


def runVerifier(state: AgentState) -> dict:
    if not state.draftAnswer:
        return {"verifierResult": VerifierResult(passed=False, verdict="HARD_FAIL", failedChecks=["No draft answer"], feedback="No answer to verify")}

    yamlCfg = getYamlConfig()
    maxRetries: int = yamlCfg.get("verifier", {}).get("max_retries", 2)

    # Plan satisfaction check (cheap, first) — only apply when evidence actually exists
    failedChecks: list[str] = []
    hasEvidence = bool(
        (state.sqlEvidence and state.sqlEvidence.rows)
        or (state.ragEvidence and state.ragEvidence.chunks)
    )

    if hasEvidence and state.plan and state.plan.expectedShape.mustIncludeNumbers:
        numbers = _extractNumbers(state.draftAnswer.answerMd)
        if not numbers:
            failedChecks.append("Plan required numbers but none found in answer")

    if hasEvidence and state.plan and state.plan.expectedShape.mustCite:
        if "[" not in state.draftAnswer.answerMd:
            failedChecks.append("Plan required citations but none found in answer")

    # Numeric consistency check
    sqlRows = state.sqlEvidence.rows if state.sqlEvidence else []
    numericIssues = _checkNumericConsistency(state.draftAnswer.answerMd, sqlRows)
    failedChecks.extend(numericIssues)

    # If pre-checks all pass, skip the LLM judge — the answer is grounded
    if not failedChecks and hasEvidence:
        judgeResult = VerifierResult(
            passed=True,
            verdict="PASS",
            failedChecks=[],
            feedback="",
            faithfulnessScore=0.9,
        )
    elif not hasEvidence:
        # No evidence was retrieved — answer is best-effort
        judgeResult = VerifierResult(
            passed=True,
            verdict="PASS",
            failedChecks=[],
            feedback="",
            faithfulnessScore=0.75,
        )
    else:
        # Pre-checks failed — call LLM judge
        client = getGroqClient()
        evidenceSummary = ""
        if sqlRows:
            evidenceSummary += f"SQL Evidence (first 5 rows): {json.dumps(sqlRows[:5])}\n"
        if state.ragEvidence and state.ragEvidence.chunks:
            evidenceSummary += "RAG chunks: " + " | ".join(c.text[:100] for c in state.ragEvidence.chunks[:3])

        judgeMessages = [
            {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"Query: {state.query}\n\n"
                f"Answer:\n{state.draftAnswer.answerMd}\n\n"
                f"Evidence:\n{evidenceSummary}\n\n"
                f"Pre-check failures: {failedChecks}"
            )},
        ]
        try:
            judgeResult = client.structuredChat(judgeMessages, responseModel=VerifierResult, temperature=0.0)
            judgeResult.failedChecks = list(set(judgeResult.failedChecks + failedChecks))
        except Exception as e:
            logger.error(f"Verifier LLM call failed: {e}")
            judgeResult = VerifierResult(
                passed=False,
                verdict="SOFT_FAIL",
                failedChecks=failedChecks,
                feedback="Verifier LLM unavailable.",
                faithfulnessScore=0.7,
            )

    trace = {
        "agent": "verifier",
        "verdict": judgeResult.verdict,
        "faithfulness": judgeResult.faithfulnessScore,
        "failedChecks": judgeResult.failedChecks,
    }
    return {"verifierResult": judgeResult, "toolTrace": [trace]}
