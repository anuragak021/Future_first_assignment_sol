"""Generates synthetic CSV datasets for the entertainment analytics platform."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT_DIR = Path(__file__).parent / "csv"
OUT_DIR.mkdir(exist_ok=True)

random.seed(42)

TITLES = [
    "Stellar Run", "Dark Orbit", "Last Kingdom", "Echo Valley",
    "Neon Nights", "Harbor Lights", "The Final Frontier", "Mirage City",
    "Crimson Tide", "Winter's Edge", "Blue Horizon", "Phantom Signal",
    "Rising Storm", "The Lost Archive", "Silver Lining",
]

GENRES = {
    "Stellar Run": "Sci-Fi",
    "Dark Orbit": "Thriller",
    "Last Kingdom": "Drama",
    "Echo Valley": "Romance",
    "Neon Nights": "Comedy",
    "Harbor Lights": "Drama",
    "The Final Frontier": "Sci-Fi",
    "Mirage City": "Thriller",
    "Crimson Tide": "Action",
    "Winter's Edge": "Drama",
    "Blue Horizon": "Romance",
    "Phantom Signal": "Sci-Fi",
    "Rising Storm": "Action",
    "The Lost Archive": "Mystery",
    "Silver Lining": "Comedy",
}

REGIONS = ["North", "South", "East", "West", "Central"]
CITIES = {
    "North": ["Oslo", "Stockholm", "Helsinki"],
    "South": ["Mumbai", "Bangalore", "Chennai"],
    "East": ["Tokyo", "Seoul", "Singapore"],
    "West": ["New York", "Los Angeles", "Chicago"],
    "Central": ["Dubai", "Istanbul", "Cairo"],
}
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS = ["Male", "Female", "Non-binary"]
TIERS = ["basic", "standard", "premium"]
CHANNELS = ["social_media", "search", "display", "email", "influencer"]
DIRECTORS = ["James Carter", "Sara Lin", "Mikhail Petrov", "Amara Diallo", "Yuki Tanaka"]


def randomDate(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def writeMovies():
    path = OUT_DIR / "movies.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title", "genre", "release_year", "director", "budget", "duration"])
        for title in TITLES:
            w.writerow([
                title,
                GENRES[title],
                random.choice([2023, 2024, 2025]),
                random.choice(DIRECTORS),
                round(random.uniform(2_000_000, 50_000_000), 2),
                random.randint(85, 150),
            ])
    print(f"  movies.csv → {len(TITLES)} rows")


def writeViewers(numViewers: int = 500):
    path = OUT_DIR / "viewers.csv"
    viewerIds = [f"V{i:04d}" for i in range(1, numViewers + 1)]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["viewer_id", "age_group", "gender", "region", "city", "subscription_tier"])
        for vid in viewerIds:
            region = random.choice(REGIONS)
            w.writerow([
                vid,
                random.choice(AGE_GROUPS),
                random.choice(GENDERS),
                region,
                random.choice(CITIES[region]),
                random.choice(TIERS),
            ])
    print(f"  viewers.csv → {numViewers} rows")
    return viewerIds


def writeWatchActivity(viewerIds: list[str], numRows: int = 3000):
    path = OUT_DIR / "watch_activity.csv"
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)

    # Stellar Run gets boosted recent activity (explains trending)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["viewer_id", "title", "watch_date", "watch_minutes", "completion_rate"])
        for _ in range(numRows):
            title = random.choice(TITLES)
            vid = random.choice(viewerIds)
            duration = random.randint(85, 150)
            completion = round(random.uniform(0.3, 1.0), 2)
            minutes = round(duration * completion, 1)

            # Boost Stellar Run in Q4 2025
            if title == "Stellar Run":
                watch_date = randomDate(date(2025, 10, 1), end)
                completion = round(random.uniform(0.7, 1.0), 2)
                minutes = round(duration * completion, 1)
            else:
                watch_date = randomDate(start, end)

            w.writerow([vid, title, watch_date.isoformat(), minutes, completion])
    print(f"  watch_activity.csv → {numRows} rows")


def writeReviews(viewerIds: list[str], numRows: int = 1200):
    path = OUT_DIR / "reviews.csv"
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["viewer_id", "title", "rating", "review_date", "sentiment"])
        for _ in range(numRows):
            title = random.choice(TITLES)
            rating = round(random.uniform(1.5, 5.0), 1)
            sentiment = "positive" if rating >= 4.0 else ("negative" if rating < 2.5 else "neutral")
            w.writerow([
                random.choice(viewerIds),
                title,
                rating,
                randomDate(start, end).isoformat(),
                sentiment,
            ])
    print(f"  reviews.csv → {numRows} rows")


def writeMarketingSpend():
    path = OUT_DIR / "marketing_spend.csv"
    periods = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title", "channel", "spend_amount", "period", "impressions", "clicks"])
        for title in TITLES:
            for period in periods:
                for channel in random.sample(CHANNELS, k=random.randint(2, 4)):
                    spend = round(random.uniform(5_000, 200_000), 2)
                    impressions = random.randint(50_000, 2_000_000)
                    clicks = random.randint(1_000, impressions // 10)
                    w.writerow([title, channel, spend, period, impressions, clicks])
    print("  marketing_spend.csv written")


def writeRegionalPerformance():
    path = OUT_DIR / "regional_performance.csv"
    periods = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region", "city", "title", "period", "total_watch_minutes", "unique_viewers", "avg_completion_rate", "revenue_estimate"])
        for period in periods:
            for region, cities in CITIES.items():
                for city in cities:
                    for title in random.sample(TITLES, k=random.randint(5, 10)):
                        w.writerow([
                            region, city, title, period,
                            round(random.uniform(10_000, 500_000), 1),
                            random.randint(100, 5_000),
                            round(random.uniform(0.4, 0.95), 2),
                            round(random.uniform(500, 50_000), 2),
                        ])
    print("  regional_performance.csv written")


if __name__ == "__main__":
    print("Generating CSV data...")
    writeMovies()
    viewerIds = writeViewers(500)
    writeWatchActivity(viewerIds, 3000)
    writeReviews(viewerIds, 1200)
    writeMarketingSpend()
    writeRegionalPerformance()
    print("Done.")
