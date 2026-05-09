"""
Transforms raw MovieLens + Netflix CSV files into the required schema:
  movies.csv · viewers.csv · watch_activity.csv
  reviews.csv · marketing_spend.csv · regional_performance.csv

Keeps the 15 fictional assignment titles alongside real MovieLens titles.
Samples rating_raw.csv (20M rows → 50K) so seed stays fast.
"""
import csv
import random
import hashlib
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

RAW = Path(__file__).parent / "csv"
OUT = RAW  # write alongside raw files

# ── Fictional titles required by the assignment ──────────────────────────────
FICTIONAL_TITLES = [
    ("Stellar Run",       "Sci-Fi",  2025, "Yuki Tanaka",     28_000_000, 112),
    ("Dark Orbit",        "Thriller",2024, "Mikhail Petrov",  18_000_000, 108),
    ("Last Kingdom",      "Drama",   2024, "James Carter",     9_000_000,  98),
    ("Echo Valley",       "Romance", 2025, "Sara Lin",         7_500_000,  94),
    ("Neon Nights",       "Comedy",  2025, "Amara Diallo",     6_000_000,  92),
    ("Harbor Lights",     "Drama",   2023, "James Carter",     8_000_000, 102),
    ("The Final Frontier","Sci-Fi",  2024, "Yuki Tanaka",     22_000_000, 130),
    ("Mirage City",       "Thriller",2025, "Mikhail Petrov",  15_000_000, 115),
    ("Crimson Tide",      "Action",  2024, "Sara Lin",        20_000_000, 120),
    ("Winter's Edge",     "Drama",   2023, "Amara Diallo",    10_000_000,  97),
    ("Blue Horizon",      "Romance", 2024, "James Carter",     8_500_000,  90),
    ("Phantom Signal",    "Sci-Fi",  2025, "Yuki Tanaka",     17_000_000, 105),
    ("Rising Storm",      "Action",  2025, "Mikhail Petrov",  24_000_000, 125),
    ("The Lost Archive",  "Mystery", 2024, "Sara Lin",         9_500_000,  99),
    ("Silver Lining",     "Comedy",  2023, "Amara Diallo",     5_500_000,  88),
]
FICTIONAL_TITLE_NAMES = {t[0] for t in FICTIONAL_TITLES}

REGIONS = ["North", "South", "East", "West", "Central"]
CITIES  = {
    "North":   ["Oslo", "Stockholm", "Helsinki"],
    "South":   ["Mumbai", "Bangalore", "Chennai"],
    "East":    ["Tokyo", "Seoul", "Singapore"],
    "West":    ["New York", "Los Angeles", "Chicago"],
    "Central": ["Dubai", "Istanbul", "Cairo"],
}
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS    = ["Male", "Female", "Non-binary"]
TIERS      = ["basic", "standard", "premium"]
CHANNELS   = ["social_media", "search", "display", "email", "influencer"]


def randomDate(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


# ── 1. movies.csv ─────────────────────────────────────────────────────────────
def buildMovies() -> dict[str, int]:
    """Returns title → internal_id mapping."""
    rows: list[dict] = []

    # Add fictional titles first (ids 1–15)
    for idx, (title, genre, year, director, budget, duration) in enumerate(FICTIONAL_TITLES, start=1):
        rows.append({
            "id": idx, "title": title, "genre": genre,
            "release_year": year, "director": director,
            "budget": budget, "duration": duration,
        })

    # Add real movies from netflix_titles_raw.csv (movies only, max 200)
    nextId = len(FICTIONAL_TITLES) + 1
    seen = set(FICTIONAL_TITLE_NAMES)
    with open(RAW / "netflix_titles_raw.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if row.get("type", "").strip() != "Movie":
                continue
            title = row["title"].strip()
            if title in seen or not title:
                continue
            duration_str = row.get("duration", "90 min").replace(" min", "").strip()
            try:
                duration = int(duration_str)
            except ValueError:
                duration = 90
            genre_raw = row.get("listed_in", "Drama").split(",")[0].strip()
            genre_map = {
                "Documentaries": "Documentary", "Dramas": "Drama",
                "Comedies": "Comedy", "Thrillers": "Thriller",
                "Action & Adventure": "Action", "Sci-Fi & Fantasy": "Sci-Fi",
                "Romantic Movies": "Romance", "Horror Movies": "Horror",
                "Mysteries": "Mystery", "Anime Features": "Anime",
                "Children & Family Movies": "Family", "Stand-Up Comedy": "Comedy",
            }
            genre = genre_map.get(genre_raw, genre_raw)
            try:
                year = int(row.get("release_year", 2020))
            except ValueError:
                year = 2020
            rows.append({
                "id": nextId, "title": title, "genre": genre,
                "release_year": year,
                "director": row.get("director", "Unknown")[:100],
                "budget": round(random.uniform(1_000_000, 50_000_000), 2),
                "duration": duration,
            })
            seen.add(title)
            nextId += 1
            if nextId > 215:
                break

    with open(OUT / "movies.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "title", "genre", "release_year", "director", "budget", "duration"])
        w.writeheader()
        w.writerows(rows)

    titleToId = {r["title"]: r["id"] for r in rows}
    print(f"  movies.csv → {len(rows)} titles ({len(FICTIONAL_TITLES)} fictional + {len(rows)-len(FICTIONAL_TITLES)} real)")
    return titleToId


# ── 2. viewers.csv ────────────────────────────────────────────────────────────
def buildViewers(maxViewers: int = 2000) -> dict[str, int]:
    """Samples real userIds from rating_raw.csv, assigns demographics."""
    viewerIds: list[str] = []
    seen: set = set()
    with open(RAW / "rating_raw.csv", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = row["userId"]
            if uid not in seen:
                viewerIds.append(uid)
                seen.add(uid)
            if len(viewerIds) >= maxViewers:
                break

    rows = []
    viewerIdToInternal: dict[str, int] = {}
    for internalId, uid in enumerate(viewerIds, start=1):
        region = random.choice(REGIONS)
        rows.append({
            "viewer_id": f"V{internalId:04d}",
            "original_user_id": uid,
            "age_group": random.choice(AGE_GROUPS),
            "gender": random.choice(GENDERS),
            "region": region,
            "city": random.choice(CITIES[region]),
            "subscription_tier": random.choice(TIERS),
        })
        viewerIdToInternal[uid] = internalId

    with open(OUT / "viewers.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["viewer_id", "original_user_id", "age_group", "gender", "region", "city", "subscription_tier"])
        w.writeheader()
        w.writerows(rows)

    vidMap = {r["original_user_id"]: r["viewer_id"] for r in rows}
    print(f"  viewers.csv → {len(rows)} viewers")
    return vidMap


# ── 3. watch_activity.csv + 4. reviews.csv ────────────────────────────────────
def buildWatchAndReviews(titleToId: dict, viewerVidMap: dict, sampleSize: int = 50_000):
    """Samples rating_raw.csv → watch_activity + reviews. Boosts Stellar Run in late 2025."""
    # Build movieId→title lookup from movie_raw.csv
    mlIdToTitle: dict[str, str] = {}
    with open(RAW / "movie_raw.csv", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            mlIdToTitle[row["movieId"]] = row["title"]

    # We also need fictional titles in mlIdToTitle — assign them fake movieIds
    fakeBase = 9_000_000
    for i, (title, *_) in enumerate(FICTIONAL_TITLES):
        mlIdToTitle[str(fakeBase + i)] = title

    # Build viewer set
    knownViewers = set(viewerVidMap.keys())

    watch_rows: list[dict] = []
    review_rows: list[dict] = []
    sampled = 0

    start2025 = date(2025, 1, 1)
    end2025   = date(2025, 12, 31)
    start2024 = date(2024, 1, 1)

    with open(RAW / "rating_raw.csv", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if sampled >= sampleSize:
                break
            uid   = row["userId"]
            mlId  = row["movieId"]
            rtg   = float(row.get("rating", 3.0))

            # Map userId → viewer_id
            if uid not in viewerVidMap:
                continue
            vid = viewerVidMap[uid]

            # Map movieId → title → our internal title
            title = mlIdToTitle.get(mlId)
            if not title or title not in titleToId:
                # Try without year suffix  e.g. "Toy Story (1995)" → "Toy Story"
                if title:
                    clean = title.rsplit("(", 1)[0].strip()
                    title = clean if clean in titleToId else None
            if not title:
                continue

            duration = random.randint(80, 140)
            completion = round(min(1.0, (rtg / 5.0) * random.uniform(0.6, 1.2)), 2)
            watch_minutes = round(duration * completion, 1)

            # Stellar Run gets boosted Q4 2025 dates
            if title == "Stellar Run":
                watch_date = randomDate(date(2025, 9, 1), end2025)
                completion = round(random.uniform(0.75, 1.0), 2)
                watch_minutes = round(duration * completion, 1)
            else:
                watch_date = randomDate(start2024, end2025)

            watch_rows.append({
                "viewer_id": vid, "title": title,
                "watch_date": watch_date.isoformat(),
                "watch_minutes": watch_minutes,
                "completion_rate": completion,
            })

            sentiment = "positive" if rtg >= 4.0 else ("negative" if rtg < 2.5 else "neutral")
            review_rows.append({
                "viewer_id": vid, "title": title,
                "rating": rtg,
                "review_date": watch_date.isoformat(),
                "sentiment": sentiment,
            })
            sampled += 1

    # Inject extra fictional-title activity (ensure all 15 have data)
    viewerList = list(viewerVidMap.values())
    for title, *_ in FICTIONAL_TITLES:
        for _ in range(random.randint(80, 200)):
            vid = random.choice(viewerList)
            watch_date = randomDate(start2025, end2025)
            if title == "Stellar Run":
                watch_date = randomDate(date(2025, 9, 1), end2025)
            completion = round(random.uniform(0.5, 1.0), 2)
            duration = 100
            watch_rows.append({
                "viewer_id": vid, "title": title,
                "watch_date": watch_date.isoformat(),
                "watch_minutes": round(duration * completion, 1),
                "completion_rate": completion,
            })
            rating = round(random.uniform(2.5, 5.0), 1)
            review_rows.append({
                "viewer_id": vid, "title": title,
                "rating": rating, "review_date": watch_date.isoformat(),
                "sentiment": "positive" if rating >= 4 else "neutral",
            })

    with open(OUT / "watch_activity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["viewer_id", "title", "watch_date", "watch_minutes", "completion_rate"])
        w.writeheader()
        w.writerows(watch_rows)

    with open(OUT / "reviews.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["viewer_id", "title", "rating", "review_date", "sentiment"])
        w.writeheader()
        w.writerows(review_rows)

    print(f"  watch_activity.csv → {len(watch_rows)} rows")
    print(f"  reviews.csv        → {len(review_rows)} rows")


# ── 5. marketing_spend.csv ────────────────────────────────────────────────────
def buildMarketingSpend(titleToId: dict):
    # Focus marketing data on fictional titles + top 20 real ones
    targetTitles = list(FICTIONAL_TITLE_NAMES) + [
        t for t in list(titleToId.keys()) if t not in FICTIONAL_TITLE_NAMES
    ][:20]
    periods = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
    rows = []
    for title in targetTitles:
        for period in periods:
            numChannels = random.randint(2, 5)
            for channel in random.sample(CHANNELS, k=numChannels):
                spend = round(random.uniform(5_000, 250_000), 2)
                # Boost Stellar Run social/influencer
                if title == "Stellar Run" and channel in ("social_media", "influencer"):
                    spend = round(random.uniform(400_000, 900_000), 2)
                impressions = random.randint(50_000, 3_000_000)
                rows.append({
                    "title": title, "channel": channel,
                    "spend_amount": spend, "period": period,
                    "impressions": impressions,
                    "clicks": random.randint(1_000, impressions // 8),
                })
    with open(OUT / "marketing_spend.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["title", "channel", "spend_amount", "period", "impressions", "clicks"])
        w.writeheader()
        w.writerows(rows)
    print(f"  marketing_spend.csv → {len(rows)} rows")


# ── 6. regional_performance.csv ───────────────────────────────────────────────
def buildRegionalPerformance(titleToId: dict):
    targetTitles = list(FICTIONAL_TITLE_NAMES) + [
        t for t in list(titleToId.keys()) if t not in FICTIONAL_TITLE_NAMES
    ][:20]
    periods = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
    rows = []
    for period in periods:
        for region, cities in CITIES.items():
            for city in cities:
                for title in random.sample(targetTitles, k=min(10, len(targetTitles))):
                    rows.append({
                        "region": region, "city": city, "title": title, "period": period,
                        "total_watch_minutes": round(random.uniform(10_000, 600_000), 1),
                        "unique_viewers": random.randint(100, 8_000),
                        "avg_completion_rate": round(random.uniform(0.4, 0.95), 2),
                        "revenue_estimate": round(random.uniform(500, 60_000), 2),
                    })
    with open(OUT / "regional_performance.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["region", "city", "title", "period", "total_watch_minutes", "unique_viewers", "avg_completion_rate", "revenue_estimate"])
        w.writeheader()
        w.writerows(rows)
    print(f"  regional_performance.csv → {len(rows)} rows")


if __name__ == "__main__":
    print("Preparing data from raw MovieLens + Netflix sources…")
    titleToId  = buildMovies()
    viewerMap  = buildViewers(maxViewers=2000)
    buildWatchAndReviews(titleToId, viewerMap, sampleSize=50_000)
    buildMarketingSpend(titleToId)
    buildRegionalPerformance(titleToId)
    print("Done. Schema CSVs written to data/csv/")
