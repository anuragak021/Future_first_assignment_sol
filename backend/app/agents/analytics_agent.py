# analyticsAgent — computes derived KPIs and chart specs from SQL evidence
import logging
from app.orchestration.state import AgentState, AnalyticsEvidence
from app.tools.analytics_tools import AnalyticsTool

logger = logging.getLogger(__name__)


def runAnalyticsAgent(state: AgentState) -> dict:
    if not state.plan:
        return {"analyticsEvidence": AnalyticsEvidence()}

    needsAnalytics = any(r.agent == "analytics" for r in state.plan.evidenceRequirements)
    if not needsAnalytics:
        return {"analyticsEvidence": AnalyticsEvidence()}

    tool = AnalyticsTool()
    sqlRows = state.sqlEvidence.rows if state.sqlEvidence else []

    kpis = tool.buildKpiSummary(sqlRows)
    chartSpecs: list[dict] = []
    summary = ""

    intent = state.plan.intent if state.plan else "fact_lookup"

    if intent in ("trend", "comparison") and sqlRows:
        hasGenre = "genre" in (sqlRows[0] if sqlRows else {})
        hasPeriod = "period" in (sqlRows[0] if sqlRows else {})

        if hasGenre and hasPeriod:
            growthData = tool.computeGenreGrowth(sqlRows)
            if growthData:
                chartSpecs.append(tool.buildBarChartSpec(
                    data=growthData,
                    xField="genre",
                    yField="latestWatchMinutes",
                    title="Watch Minutes by Genre",
                ))
                kpis["fastestGrowingGenre"] = max(growthData, key=lambda x: x.get("periodGrowthRate", 0)).get("genre", "")
        elif sqlRows and "title" in sqlRows[0]:
            chartSpecs.append(tool.buildBarChartSpec(
                data=sqlRows[:10],
                xField="title",
                yField=list(sqlRows[0].keys())[-1] if sqlRows else "value",
                title="Top Titles Performance",
            ))

    if intent == "comparison" and sqlRows:
        titles = list({r.get("title", "") for r in sqlRows if r.get("title")})
        if len(titles) >= 2:
            summary = f"Comparing {titles[0]} vs {titles[1]} across key metrics."

    trace = {"agent": "analytics_agent", "kpiCount": len(kpis), "chartCount": len(chartSpecs)}
    return {
        "analyticsEvidence": AnalyticsEvidence(kpis=kpis, chartSpecs=chartSpecs, summary=summary),
        "toolTrace": [trace],
    }
