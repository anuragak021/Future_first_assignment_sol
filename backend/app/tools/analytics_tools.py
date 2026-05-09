# analyticsTools — derived metrics (growth, momentum, share) and Vega-Lite chart specs
import logging
import pandas as pd
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class AnalyticsTool:
    """Transforms raw SQL rows into KPIs and chart specs. No LLM math."""

    def computeGenreGrowth(self, genreTrendRows: list[dict]) -> list[dict]:
        if not genreTrendRows:
            return []
        df = pd.DataFrame(genreTrendRows)
        df["period"] = pd.to_datetime(df["period"])
        df = df.sort_values(["genre", "period"])
        df["prev"] = df.groupby("genre")["watchMinutes"].shift(1)
        df["growth"] = (df["watchMinutes"] - df["prev"]) / df["prev"].replace(0, np.nan)
        df["growth"] = df["growth"].fillna(0)
        latest = df.groupby("genre").last().reset_index()
        return latest[["genre", "watchMinutes", "growth"]].rename(
            columns={"watchMinutes": "latestWatchMinutes", "growth": "periodGrowthRate"}
        ).to_dict(orient="records")

    def computeTitleMomentum(self, watchRows: list[dict]) -> dict:
        if not watchRows:
            return {}
        df = pd.DataFrame(watchRows)
        df["period"] = pd.to_datetime(df.get("period", pd.Series(dtype=str)))
        if df.empty:
            return {}
        recentHalf = df.tail(len(df) // 2 + 1)
        olderHalf = df.head(max(1, len(df) // 2))
        recentAvg = recentHalf["watchMinutes"].mean() if "watchMinutes" in recentHalf else 0
        olderAvg = olderHalf["watchMinutes"].mean() if "watchMinutes" in olderHalf else 0
        momentum = float((recentAvg - olderAvg) / max(olderAvg, 1))
        return {"recentAvgMinutes": float(recentAvg), "olderAvgMinutes": float(olderAvg), "momentumScore": momentum}

    def buildBarChartSpec(
        self,
        data: list[dict],
        xField: str,
        yField: str,
        title: str,
        color: str = "#4F81BD",
    ) -> dict:
        return {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": title,
            "mark": "bar",
            "data": {"values": data},
            "encoding": {
                "x": {"field": xField, "type": "nominal", "sort": "-y", "axis": {"labelAngle": -45}},
                "y": {"field": yField, "type": "quantitative"},
                "color": {"value": color},
                "tooltip": [{"field": xField}, {"field": yField}],
            },
            "width": 500,
            "height": 300,
        }

    def buildLineChartSpec(
        self,
        data: list[dict],
        xField: str,
        yField: str,
        colorField: Optional[str],
        title: str,
    ) -> dict:
        spec: dict = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": title,
            "mark": "line",
            "data": {"values": data},
            "encoding": {
                "x": {"field": xField, "type": "temporal"},
                "y": {"field": yField, "type": "quantitative"},
                "tooltip": [{"field": xField}, {"field": yField}],
            },
            "width": 500,
            "height": 300,
        }
        if colorField:
            spec["encoding"]["color"] = {"field": colorField, "type": "nominal"}
        return spec

    def buildKpiSummary(self, data: list[dict]) -> dict[str, float]:
        if not data:
            return {}
        df = pd.DataFrame(data)
        kpis: dict[str, float] = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            kpis[f"total_{col}"] = float(df[col].sum())
            kpis[f"avg_{col}"] = float(df[col].mean())
        return kpis
