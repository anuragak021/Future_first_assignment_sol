# sqlTools — parameterized query templates; the LLM never constructs raw SQL
import logging
from datetime import date
from typing import Literal, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MetricLiteral = Literal["watch_minutes", "completion_rate", "revenue", "unique_viewers"]
GranularityLiteral = Literal["week", "month"]


class SqlToolRegistry:
    """All structured-data access goes through this registry — no raw SQL outside here."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def getTopTitles(
        self,
        year: int,
        metric: MetricLiteral = "watch_minutes",
        limit: int = 10,
    ) -> list[dict]:
        metricCol = {
            "watch_minutes": "SUM(wa.watch_minutes)",
            "completion_rate": "AVG(wa.completion_rate)",
            "revenue": "SUM(rp.revenue_estimate)",
            "unique_viewers": "COUNT(DISTINCT wa.viewer_id)",
        }[metric]
        sql = text(f"""
            SELECT m.title, m.genre, {metricCol} AS metric_value
            FROM movies m
            JOIN watch_activity wa ON wa.movie_id = m.id
            LEFT JOIN regional_performance rp ON rp.movie_id = m.id
            WHERE strftime('%Y', wa.watch_date) = :year
            GROUP BY m.id, m.title, m.genre
            ORDER BY metric_value DESC
            LIMIT :limit
        """)
        result = await self._session.execute(sql, {"year": str(year), "limit": limit})
        return [{"title": r.title, "genre": r.genre, "metric": metric, "value": float(r.metric_value or 0)} for r in result]

    async def getGenreTrends(
        self,
        startDate: date,
        endDate: date,
        granularity: GranularityLiteral = "month",
    ) -> list[dict]:
        fmtStr = "%Y-%m" if granularity == "month" else "%Y-%W"
        sql = text(f"""
            SELECT m.genre,
                   strftime('{fmtStr}', wa.watch_date) AS period,
                   SUM(wa.watch_minutes) AS total_watch_minutes,
                   COUNT(DISTINCT wa.viewer_id) AS unique_viewers
            FROM movies m
            JOIN watch_activity wa ON wa.movie_id = m.id
            WHERE wa.watch_date BETWEEN :start AND :end
            GROUP BY m.genre, period
            ORDER BY m.genre, period
        """)
        result = await self._session.execute(sql, {"start": startDate, "end": endDate})
        return [
            {"genre": r.genre, "period": str(r.period), "watchMinutes": float(r.total_watch_minutes or 0), "uniqueViewers": int(r.unique_viewers or 0)}
            for r in result
        ]

    async def getRegionalPerformance(
        self,
        region: Optional[str],
        period: str,
    ) -> list[dict]:
        sql = text("""
            SELECT region, city, SUM(total_watch_minutes) AS watch_minutes,
                   SUM(unique_viewers) AS viewers,
                   AVG(avg_completion_rate) AS completion_rate,
                   SUM(revenue_estimate) AS revenue
            FROM regional_performance
            WHERE period = :period
            AND (:region IS NULL OR region = :region)
            GROUP BY region, city
            ORDER BY watch_minutes DESC
        """)
        result = await self._session.execute(sql, {"period": period, "region": region})
        return [
            {"region": r.region, "city": r.city, "watchMinutes": float(r.watch_minutes or 0),
             "viewers": int(r.viewers or 0), "completionRate": float(r.completion_rate or 0),
             "revenue": float(r.revenue or 0)}
            for r in result
        ]

    async def compareTitles(
        self,
        titleA: str,
        titleB: str,
        metrics: Optional[list[str]] = None,
    ) -> dict:
        sql = text("""
            SELECT m.title,
                   SUM(wa.watch_minutes) AS total_watch_minutes,
                   AVG(wa.completion_rate) AS avg_completion_rate,
                   COUNT(DISTINCT wa.viewer_id) AS unique_viewers,
                   AVG(r.rating) AS avg_rating,
                   SUM(ms.spend_amount) AS total_marketing_spend
            FROM movies m
            LEFT JOIN watch_activity wa ON wa.movie_id = m.id
            LEFT JOIN reviews r ON r.movie_id = m.id
            LEFT JOIN marketing_spend ms ON ms.movie_id = m.id
            WHERE m.title IN (:titleA, :titleB)
            GROUP BY m.id, m.title
        """)
        result = await self._session.execute(sql, {"titleA": titleA, "titleB": titleB})
        rows = result.fetchall()
        comparison = {}
        for row in rows:
            comparison[row.title] = {
                "watchMinutes": float(row.total_watch_minutes or 0),
                "completionRate": float(row.avg_completion_rate or 0),
                "uniqueViewers": int(row.unique_viewers or 0),
                "avgRating": float(row.avg_rating or 0),
                "marketingSpend": float(row.total_marketing_spend or 0),
            }
        return comparison

    async def getMarketingEfficiency(
        self,
        title: Optional[str],
        period: str,
    ) -> list[dict]:
        sql = text("""
            SELECT m.title, ms.channel, ms.spend_amount,
                   ms.impressions, ms.clicks,
                   CASE WHEN ms.spend_amount > 0 THEN ms.clicks::float / ms.spend_amount ELSE 0 END AS cpc
            FROM marketing_spend ms
            JOIN movies m ON m.id = ms.movie_id
            WHERE ms.period = :period
            AND (:title IS NULL OR m.title = :title)
            ORDER BY ms.spend_amount DESC
        """)
        result = await self._session.execute(sql, {"period": period, "title": title})
        return [
            {"title": r.title, "channel": r.channel, "spendAmount": float(r.spend_amount),
             "impressions": int(r.impressions or 0), "clicks": int(r.clicks or 0), "cpc": float(r.cpc or 0)}
            for r in result
        ]

    async def getAudienceSegments(self, year: int) -> list[dict]:
        sql = text("""
            SELECT v.age_group, v.gender, v.subscription_tier,
                   COUNT(DISTINCT wa.viewer_id) AS viewers,
                   AVG(wa.completion_rate) AS avg_completion,
                   SUM(wa.watch_minutes) AS total_minutes
            FROM watch_activity wa
            JOIN viewers v ON v.id = wa.viewer_id
            WHERE strftime('%Y', wa.watch_date) = :year
            GROUP BY v.age_group, v.gender, v.subscription_tier
            ORDER BY viewers DESC
        """)
        result = await self._session.execute(sql, {"year": str(year)})
        return [
            {"ageGroup": r.age_group, "gender": r.gender, "tier": r.subscription_tier,
             "viewers": int(r.viewers), "avgCompletion": float(r.avg_completion or 0),
             "totalMinutes": float(r.total_minutes or 0)}
            for r in result
        ]
