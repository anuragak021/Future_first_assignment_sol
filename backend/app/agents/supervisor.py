# supervisor — classifies intent and emits a typed Plan contract
import logging
from app.llm.groq_client import getGroqClient
from app.orchestration.state import AgentState, Plan, EvidenceRequirement, ExpectedAnswerShape

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a routing supervisor for an internal analytics assistant.
Given a user query, produce a JSON plan with evidenceRequirements.

Rules:
- ALWAYS include "sql" in evidenceRequirements for any question about titles, performance, trends, regions, genres, or audience.
- ALWAYS include "rag" for questions about strategy, recommendations, leadership, policy, or explanations.
- Include "analytics" for trend or comparison questions.
- For greetings or off-topic queries, return an empty evidenceRequirements list.
- mustCite should be true only when sql or rag evidence is expected.
"""


def runSupervisor(state: AgentState) -> dict:
    client = getGroqClient()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Query: {state.query}"},
    ]

    try:
        plan = client.structuredChat(messages, responseModel=Plan, temperature=0.2)
    except Exception as e:
        logger.error(f"Supervisor failed: {e}")
        plan = Plan(
            intent="fact_lookup",
            evidenceRequirements=[
                EvidenceRequirement(agent="sql", purpose="general lookup", mustReturn=["title"], minRows=1),
                EvidenceRequirement(agent="rag", purpose="context from documents", mustReturn=["text"], minRows=1),
            ],
            expectedShape=ExpectedAnswerShape(mustCite=True, mustIncludeNumbers=False, mustIncludeChart=False),
            parallel=True,
            rationale="fallback plan due to supervisor error",
        )

    trace = {"agent": "supervisor", "plan": plan.model_dump()}
    return {"plan": plan, "toolTrace": [trace]}
