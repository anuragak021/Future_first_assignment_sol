# sqlAgent — calls parameterized SQL tools based on the Supervisor's plan
import logging
from datetime import date
from app.llm.groq_client import getGroqClient
from app.orchestration.state import AgentState, SqlEvidence
from app.observability.trace_store import getTraceStore

logger = logging.getLogger(__name__)

TOOL_DESCRIPTIONS = [
    {
        "type": "function",
        "function": {
            "name": "getTopTitles",
            "description": "Get top performing titles for a given year and metric",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "4-digit year e.g. 2025"},
                    "metric": {"type": "string", "enum": ["watch_minutes", "completion_rate", "revenue", "unique_viewers"]},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compareTitles",
            "description": "Compare two titles across all performance metrics",
            "parameters": {
                "type": "object",
                "properties": {
                    "titleA": {"type": "string"},
                    "titleB": {"type": "string"},
                },
                "required": ["titleA", "titleB"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getGenreTrends",
            "description": "Get genre-level watch trends over a date range",
            "parameters": {
                "type": "object",
                "properties": {
                    "startDate": {"type": "string", "description": "ISO date e.g. 2025-01-01"},
                    "endDate": {"type": "string", "description": "ISO date e.g. 2025-12-31"},
                    "granularity": {"type": "string", "enum": ["week", "month"]},
                },
                "required": ["startDate", "endDate"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getRegionalPerformance",
            "description": "Get engagement and revenue by region/city for a period",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "e.g. 2025-Q1 or 2025-03"},
                    "region": {"type": "string", "description": "optional region filter"},
                },
                "required": ["period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getAudienceSegments",
            "description": "Get viewer engagement broken down by age group, gender, subscription tier",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer"},
                },
                "required": ["year"],
            },
        },
    },
]


async def runSqlAgent(state: AgentState, sqlToolRegistry) -> dict:
    if not state.plan:
        return {"sqlEvidence": SqlEvidence()}

    needsSql = any(r.agent == "sql" for r in state.plan.evidenceRequirements)
    if not needsSql:
        return {"sqlEvidence": SqlEvidence()}

    client = getGroqClient()
    messages = [
        {"role": "system", "content": (
            "You are an SQL data retrieval agent for an entertainment analytics platform. "
            "Use the available tools to retrieve the exact data needed to answer the query. "
            "Call only the tools necessary. Do not make up data."
        )},
        {"role": "user", "content": f"Query: {state.query}\nPlan rationale: {state.plan.rationale}"},
    ]

    rows: list[dict] = []
    toolName = ""
    toolParams: dict = {}
    traceEntries: list[dict] = []

    import json
    response = client.chat(messages, temperature=0.0, tools=TOOL_DESCRIPTIONS, toolChoice="auto")
    toolCalls = response.choices[0].message.tool_calls or []

    for toolCall in toolCalls:
        fnName = toolCall.function.name
        fnArgs = json.loads(toolCall.function.arguments)
        toolName = fnName
        toolParams = fnArgs

        try:
            if fnName == "getTopTitles":
                result = await sqlToolRegistry.getTopTitles(
                    year=fnArgs.get("year", 2025),
                    metric=fnArgs.get("metric", "watch_minutes"),
                    limit=fnArgs.get("limit", 10),
                )
            elif fnName == "compareTitles":
                result = list(
                    (await sqlToolRegistry.compareTitles(
                        titleA=fnArgs["titleA"],
                        titleB=fnArgs["titleB"],
                    )).items()
                )
                result = [{"title": k, **v} for k, v in (await sqlToolRegistry.compareTitles(
                    titleA=fnArgs["titleA"], titleB=fnArgs["titleB"]
                )).items()]
            elif fnName == "getGenreTrends":
                result = await sqlToolRegistry.getGenreTrends(
                    startDate=date.fromisoformat(fnArgs["startDate"]),
                    endDate=date.fromisoformat(fnArgs["endDate"]),
                    granularity=fnArgs.get("granularity", "month"),
                )
            elif fnName == "getRegionalPerformance":
                result = await sqlToolRegistry.getRegionalPerformance(
                    region=fnArgs.get("region"),
                    period=fnArgs["period"],
                )
            elif fnName == "getAudienceSegments":
                result = await sqlToolRegistry.getAudienceSegments(year=fnArgs.get("year", 2025))
            else:
                result = []

            rows.extend(result if isinstance(result, list) else [result])
            traceEntries.append({"tool": fnName, "params": fnArgs, "rowCount": len(result) if isinstance(result, list) else 1})
            logger.info(f"SQL tool {fnName} returned {len(result) if isinstance(result, list) else 1} rows")

        except Exception as e:
            logger.error(f"SQL tool {fnName} failed: {e}")
            state.errors.append(f"SQL tool error: {e}")

    evidence = SqlEvidence(rows=rows, toolName=toolName, params=toolParams)
    return {"sqlEvidence": evidence, "toolTrace": [{"agent": "sql_agent", "calls": traceEntries}]}
