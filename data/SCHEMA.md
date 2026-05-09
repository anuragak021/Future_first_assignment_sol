# Data Schema

## SQL Tables

### movies
| Column | Type | Description |
|--------|------|-------------|
| id | PK | Auto-increment |
| title | VARCHAR | Movie title |
| genre | VARCHAR | Genre |
| release_year | INT | 4-digit year |
| director | VARCHAR | Director name |
| budget | FLOAT | Production budget USD |
| duration | INT | Runtime in minutes |

### viewers
| Column | Type | Description |
|--------|------|-------------|
| id | PK | Auto-increment |
| age_group | VARCHAR | 18-24, 25-34, 35-44, 45-54, 55+ |
| gender | VARCHAR | Male / Female / Non-binary |
| region | VARCHAR | North / South / East / West / Central |
| city | VARCHAR | City name |
| subscription_tier | VARCHAR | basic / standard / premium |

> **Privacy**: viewer emails and names are not stored. viewer_id in CSVs is a synthetic key.

### watch_activity
| Column | Type | Description |
|--------|------|-------------|
| id | PK | |
| movie_id | FK → movies.id | |
| viewer_id | FK → viewers.id | |
| watch_date | DATE | |
| watch_minutes | FLOAT | Minutes watched |
| completion_rate | FLOAT | 0.0–1.0 |

### reviews
| Column | Type | Description |
|--------|------|-------------|
| movie_id | FK | |
| viewer_id | FK | |
| rating | FLOAT | 1.0–5.0 |
| review_date | DATE | |
| sentiment | VARCHAR | positive / neutral / negative |

### marketing_spend
| Column | Type | Description |
|--------|------|-------------|
| movie_id | FK | |
| channel | VARCHAR | social_media / search / display / email / influencer |
| spend_amount | FLOAT | USD |
| period | VARCHAR | e.g. 2025-Q1 |
| impressions | INT | |
| clicks | INT | |

### regional_performance
| Column | Type | Description |
|--------|------|-------------|
| region | VARCHAR | |
| city | VARCHAR | |
| movie_id | FK (nullable) | |
| period | VARCHAR | |
| total_watch_minutes | FLOAT | |
| unique_viewers | INT | |
| avg_completion_rate | FLOAT | |
| revenue_estimate | FLOAT | USD |

## PDF Documents

| File | Contents |
|------|----------|
| quarterly_executive_report.pdf | Q3 2025 KPIs, top titles, genre analysis, regional highlights |
| campaign_performance_summary.pdf | Q4 2025 marketing campaign results by title and channel |
| content_roadmap_2026.pdf | Greenlit projects, comedy reboot plan, localization strategy |
| policy_guidelines.pdf | Data access policy, AI policy, third-party integration rules |
| audience_behavior_report.pdf | Demographics, churn analysis, recommendation engine impact |
