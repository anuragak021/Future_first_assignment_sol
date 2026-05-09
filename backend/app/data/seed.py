# seed — loads schema CSVs into the configured database (SQLite or Postgres)
import asyncio
import csv
import sys
import logging
from datetime import date
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import getSettings
from app.data.schema import Base, Movie, Viewer, WatchActivity, Review, MarketingSpend, RegionalPerformance

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "csv"


def _date(s: str) -> date:
    return date.fromisoformat(s) if s else None


async def dropAndCreate(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def seedMovies(session: AsyncSession) -> dict[str, int]:
    """Returns title → db_id map."""
    titleToId: dict[str, int] = {}
    with open(DATA_DIR / "movies.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movie = Movie(
                title=row["title"],
                genre=row["genre"],
                releaseYear=int(row["release_year"]),
                director=row.get("director", ""),
                budget=float(row.get("budget") or 0),
                duration=int(row.get("duration") or 90),
            )
            session.add(movie)
            await session.flush()
            titleToId[row["title"]] = movie.id
    logger.info(f"Seeded {len(titleToId)} movies")
    return titleToId


async def seedViewers(session: AsyncSession) -> dict[str, int]:
    """Returns viewer_id string (V0001) → db_id map."""
    vidToId: dict[str, int] = {}
    with open(DATA_DIR / "viewers.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            viewer = Viewer(
                ageGroup=row["age_group"],
                gender=row.get("gender", ""),
                region=row.get("region", ""),
                city=row.get("city", ""),
                subscriptionTier=row.get("subscription_tier", "basic"),
            )
            session.add(viewer)
            await session.flush()
            vidToId[row["viewer_id"]] = viewer.id
    logger.info(f"Seeded {len(vidToId)} viewers")
    return vidToId


async def seedWatchActivity(session: AsyncSession, movieMap: dict, viewerMap: dict) -> None:
    count = 0
    with open(DATA_DIR / "watch_activity.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movieId = movieMap.get(row["title"])
            viewerId = viewerMap.get(row["viewer_id"])
            if not movieId or not viewerId:
                continue
            session.add(WatchActivity(
                movieId=movieId,
                viewerId=viewerId,
                watchDate=_date(row["watch_date"]),
                watchMinutes=float(row["watch_minutes"]),
                completionRate=float(row["completion_rate"]),
            ))
            count += 1
    logger.info(f"Seeded {count} watch activity rows")


async def seedReviews(session: AsyncSession, movieMap: dict, viewerMap: dict) -> None:
    count = 0
    with open(DATA_DIR / "reviews.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movieId = movieMap.get(row["title"])
            viewerId = viewerMap.get(row["viewer_id"])
            if not movieId or not viewerId:
                continue
            session.add(Review(
                movieId=movieId,
                viewerId=viewerId,
                rating=float(row["rating"]),
                reviewDate=_date(row["review_date"]),
                sentiment=row.get("sentiment", "neutral"),
            ))
            count += 1
    logger.info(f"Seeded {count} review rows")


async def seedMarketingSpend(session: AsyncSession, movieMap: dict) -> None:
    count = 0
    with open(DATA_DIR / "marketing_spend.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movieId = movieMap.get(row["title"])
            if not movieId:
                continue
            session.add(MarketingSpend(
                movieId=movieId,
                channel=row["channel"],
                spendAmount=float(row["spend_amount"]),
                period=row["period"],
                impressions=int(row.get("impressions") or 0),
                clicks=int(row.get("clicks") or 0),
            ))
            count += 1
    logger.info(f"Seeded {count} marketing spend rows")


async def seedRegionalPerformance(session: AsyncSession, movieMap: dict) -> None:
    count = 0
    with open(DATA_DIR / "regional_performance.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            movieId = movieMap.get(row.get("title", ""))
            session.add(RegionalPerformance(
                region=row["region"],
                city=row["city"],
                movieId=movieId,
                period=row["period"],
                totalWatchMinutes=float(row.get("total_watch_minutes") or 0),
                uniqueViewers=int(row.get("unique_viewers") or 0),
                avgCompletionRate=float(row.get("avg_completion_rate") or 0),
                revenueEstimate=float(row.get("revenue_estimate") or 0),
            ))
            count += 1
    logger.info(f"Seeded {count} regional performance rows")


async def runSeed() -> None:
    settings = getSettings()
    connectArgs = {"check_same_thread": False} if settings.use_sqlite else {}
    engine = create_async_engine(settings.databaseUrl, echo=False, connect_args=connectArgs)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    logger.info(f"Dropping and recreating schema on {settings.databaseUrl[:40]}…")
    await dropAndCreate(engine)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            movieMap = await seedMovies(session)
            viewerMap = await seedViewers(session)
            await seedWatchActivity(session, movieMap, viewerMap)
            await seedReviews(session, movieMap, viewerMap)
            await seedMarketingSpend(session, movieMap)
            await seedRegionalPerformance(session, movieMap)

    logger.info("Seed complete.")
    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(runSeed())
