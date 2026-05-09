"""Generates synthetic PDF documents for the RAG knowledge base."""
from pathlib import Path
from fpdf import FPDF

OUT_DIR = Path(__file__).parent / "pdfs"
OUT_DIR.mkdir(exist_ok=True)


def makePdf(filename: str, title: str, sections: list[tuple[str, str]]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, body)
        pdf.ln(4)
    pdf.output(str(OUT_DIR / filename))
    print(f"  {filename} written")


QUARTERLY_REPORT = [
    ("Executive Summary", (
        "FictStream Q3 2025 delivered record watch-minute growth of 23% YoY. "
        "Stellar Run became the fastest-growing title in platform history, driven by "
        "aggressive social media marketing and a viral recommendation loop in the 18-34 demographic. "
        "Comedy titles underperformed by 12% versus forecast, primarily in the South and Central regions. "
        "Premium subscriptions grew 8% while basic-tier churn rose to 4.2%."
    )),
    ("Top Performing Titles", (
        "1. Stellar Run - 2.1M watch hours, 89% completion rate, 4.7/5 avg rating. "
        "Spike in Q4 driven by influencer campaigns across East and West regions. "
        "2. Dark Orbit - 1.8M watch hours, 82% completion. Strong thriller audience in 35-44 segment. "
        "3. Last Kingdom - 1.6M watch hours, drama genre leader in North region."
    )),
    ("Genre Analysis", (
        "Sci-Fi and Thriller genres show strongest momentum with 31% and 19% QoQ growth respectively. "
        "Comedy declined 12%: audience surveys indicate content quality concerns and poor pacing. "
        "Drama holds steady at 15% of total watch hours. "
        "Action genre spiked in Q3 driven by the Rising Storm release."
    )),
    ("Marketing Effectiveness", (
        "Social media spend ROI was 3.2x vs 2.1x for display advertising. "
        "Influencer campaigns for Stellar Run generated 12M impressions at $0.004 CPC. "
        "Email marketing shows declining open rates (18% vs 24% prior year). "
        "Recommendation: shift 20% of display budget to social/influencer for Q4."
    )),
    ("Regional Highlights", (
        "East region (Tokyo, Seoul, Singapore) leads engagement with avg completion rate of 0.87. "
        "West region (New York, LA, Chicago) drives highest revenue at $2.1M quarterly. "
        "South region underperforms on comedy titles; drama and action perform well. "
        "Central region (Dubai, Istanbul, Cairo) is fastest-growing at 34% QoQ viewer growth."
    )),
    ("Leadership Recommendations", (
        "1. Greenlight two additional Sci-Fi productions for 2026 H1 to capitalize on genre momentum. "
        "2. Commission a comedy content quality review - current slate not resonating with target demographic. "
        "3. Increase influencer marketing budget by 25% for Q1 2026. "
        "4. Invest in retention initiatives for basic-tier subscribers (personalization, exclusive previews). "
        "5. Expand localized content for Central region given its growth trajectory."
    )),
]

CAMPAIGN_SUMMARY = [
    ("Campaign Overview Q4 2025", (
        "Total marketing spend Q4 2025: $4.2M across all titles and channels. "
        "Primary focus: Stellar Run launch amplification and Dark Orbit retention campaign."
    )),
    ("Stellar Run Campaign", (
        "Budget: $1.8M. Channels: influencer (45%), social media (35%), display (20%). "
        "Results: 18M impressions, 2.1M clicks, 340K new trial sign-ups attributed. "
        "CPA: $5.29. Best performing influencer segment: gaming/tech creators on YouTube. "
        "Stellar Run trended on social media for 11 consecutive days post-launch."
    )),
    ("Dark Orbit Retention Campaign", (
        "Budget: $600K. Target: users who completed >=50% of Season 1. "
        "Email + push notification series drove 28% reactivation rate. "
        "Average watch time increased 40% among retargeted users in 30-day window."
    )),
    ("Comedy Genre Campaign", (
        "Budget: $400K across Neon Nights and Silver Lining. "
        "Performance below expectations: CTR 0.8% vs 1.4% platform average. "
        "Audience feedback: trailers not communicating quality improvement. "
        "Recommendation: pause paid comedy acquisition; invest in organic social content."
    )),
    ("Channel Performance Table", (
        "Social Media: $1.4M spend, 3.4x ROAS, best for 18-34 demo. "
        "Influencer: $1.1M spend, 3.9x ROAS, best for Sci-Fi and Action. "
        "Display: $900K spend, 1.8x ROAS, declining effectiveness. "
        "Search: $500K spend, 2.6x ROAS, strong for intent-driven titles. "
        "Email: $300K spend, 2.1x ROAS, effective for retention, not acquisition."
    )),
]

CONTENT_ROADMAP = [
    ("2026 Content Strategy", (
        "FictStream 2026 content investment: $180M total, up 22% from 2025. "
        "Focus areas: Sci-Fi expansion (6 new titles), Drama prestige slate (4 titles), "
        "Action tentpoles (3 titles), Comedy reboot (2 titles with new showrunners)."
    )),
    ("Greenlit Projects", (
        "Stellar Run Season 2 - $28M production budget, targeting Q2 2026 release. "
        "Dark Orbit: Origins - prequel series, $18M, Q3 2026. "
        "Phantom Signal - new Sci-Fi IP, $15M, Q1 2026. "
        "Echo Valley Season 2 - Romance drama, $9M, Q2 2026."
    )),
    ("Comedy Reboot Plan", (
        "Two new comedy projects with talent from streaming-native comedy background. "
        "Audience research indicates preference for observational comedy over slapstick. "
        "Target demographic: 25-34 urban professionals. "
        "Both projects have female-led creative teams to address diversity gap."
    )),
    ("Localization Strategy", (
        "Dubbing and subtitle investment: $12M for 14 languages. "
        "Priority markets: Central region (Arabic, Turkish), East (Japanese, Korean). "
        "Local originals pilot: 2 productions in East region for authenticity."
    )),
]

POLICY_GUIDELINES = [
    ("Data Access Policy", (
        "All viewer data is classified as PII and subject to GDPR and local equivalents. "
        "Viewer emails, names, and payment details must not be exposed in analytics queries. "
        "Aggregated viewer data (age group, region, tier) is approved for analytics use. "
        "Individual viewer profiles require explicit DPO approval before access."
    )),
    ("Content Rating Guidelines", (
        "All content must carry an audience rating: G, PG, PG-13, R, or NC-17. "
        "Parental control features are mandatory on all family subscription tiers. "
        "Marketing materials must reflect the content rating of the advertised title."
    )),
    ("AI and Recommendation Policy", (
        "AI-driven recommendations must not discriminate based on protected characteristics. "
        "Recommendation bias audits are conducted quarterly by the Trust & Safety team. "
        "All AI-generated content summaries must be clearly labeled. "
        "User data used for recommendations is anonymized at the feature extraction stage."
    )),
    ("Third-Party Integration Policy", (
        "All third-party APIs used in production require security review. "
        "Vendor data sharing agreements must be reviewed by Legal before implementation. "
        "External analytics tools may receive only aggregated, de-identified datasets."
    )),
]

AUDIENCE_BEHAVIOR = [
    ("Viewer Engagement Patterns", (
        "Peak viewing hours: 7PM-11PM local time across all regions. "
        "Mobile viewing accounts for 58% of total watch minutes, up from 51% in 2024. "
        "Average session length: 47 minutes. Users watching on TV have 23% higher completion rates."
    )),
    ("Demographic Insights", (
        "18-24 demographic: highest binge-watching rate (3.2 episodes per session), "
        "lowest subscription retention (62% 12-month retention). "
        "25-34 demographic: highest LTV, strongest drama and Sci-Fi affinity. "
        "35-44 demographic: most likely to recommend to friends, highest premium tier rate (34%). "
        "55+ demographic: fastest growing segment, +18% YoY, strong drama and mystery preference."
    )),
    ("Genre Preference by Region", (
        "North region: Drama (38%), Sci-Fi (28%), Mystery (18%). "
        "South region: Action (35%), Drama (30%), Comedy (20%). "
        "East region: Sci-Fi (42%), Thriller (25%), Romance (18%). "
        "West region: Thriller (33%), Action (28%), Sci-Fi (22%). "
        "Central region: Drama (40%), Romance (25%), Action (20%)."
    )),
    ("Churn Analysis", (
        "Main churn drivers: content gaps between releases (42%), price sensitivity (31%), "
        "technical issues (14%), content quality concerns (13%). "
        "Titles with completion rate >80% reduce churn by 18% in the 30 days post-watch. "
        "Comedy genre has highest churn correlation: users who only watch comedy are 2.3x more likely to churn."
    )),
    ("Recommendation Engine Impact", (
        "Personalized recommendations drive 67% of all watch starts. "
        "Cold-start problem: new users take avg 4.2 sessions to receive high-quality recommendations. "
        "Genre diversity in recommendations reduces churn by 9% versus single-genre recommendation. "
        "Stellar Run success partially attributable to recommendation engine surfacing it to Sci-Fi finishers."
    )),
]


if __name__ == "__main__":
    print("Generating PDF documents...")
    makePdf("quarterly_executive_report.pdf", "FictStream Q3 2025 Executive Report", QUARTERLY_REPORT)
    makePdf("campaign_performance_summary.pdf", "Q4 2025 Marketing Campaign Summary", CAMPAIGN_SUMMARY)
    makePdf("content_roadmap_2026.pdf", "FictStream 2026 Content Roadmap", CONTENT_ROADMAP)
    makePdf("policy_guidelines.pdf", "FictStream Data & Content Policy Guidelines", POLICY_GUIDELINES)
    makePdf("audience_behavior_report.pdf", "FictStream Audience Behavior Analysis 2025", AUDIENCE_BEHAVIOR)
    print("Done.")
