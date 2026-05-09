# unit tests for AnalyticsTool — no external dependencies needed
import pytest
from app.tools.analytics_tools import AnalyticsTool


@pytest.fixture
def tool():
    return AnalyticsTool()


def test_buildKpiSummary_empty(tool):
    assert tool.buildKpiSummary([]) == {}


def test_buildKpiSummary_numeric(tool):
    data = [{"value": 10.0}, {"value": 20.0}]
    kpis = tool.buildKpiSummary(data)
    assert kpis["total_value"] == 30.0
    assert kpis["avg_value"] == 15.0


def test_buildBarChartSpec_schema(tool):
    spec = tool.buildBarChartSpec(
        data=[{"title": "A", "value": 100}],
        xField="title",
        yField="value",
        title="Test Chart",
    )
    assert spec["mark"] == "bar"
    assert spec["encoding"]["x"]["field"] == "title"
    assert spec["encoding"]["y"]["field"] == "value"


def test_computeGenreGrowth_returns_list(tool):
    rows = [
        {"genre": "Sci-Fi", "period": "2025-01-01", "watchMinutes": 1000, "uniqueViewers": 50},
        {"genre": "Sci-Fi", "period": "2025-02-01", "watchMinutes": 1300, "uniqueViewers": 60},
        {"genre": "Comedy", "period": "2025-01-01", "watchMinutes": 500, "uniqueViewers": 30},
        {"genre": "Comedy", "period": "2025-02-01", "watchMinutes": 480, "uniqueViewers": 28},
    ]
    result = tool.computeGenreGrowth(rows)
    assert isinstance(result, list)
    assert len(result) == 2
    scifi = next(r for r in result if r["genre"] == "Sci-Fi")
    assert scifi["periodGrowthRate"] == pytest.approx(0.3, rel=0.01)
