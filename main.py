import os
from datetime import datetime
from pytrends.request import TrendReq

# --------------------
# Config
# --------------------
REGION = "GB"  # United Kingdom
MAX_TRENDS = 20

# --------------------
# Helpers
# --------------------
def ensure_reports_dir():
    os.makedirs("reports", exist_ok=True)

def report_path():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return f"reports/report_{ts}.md"

def write_header(f):
    f.write("# Daily Trend → MakerWorld Report\n\n")
    f.write(f"- Date (UTC): {datetime.utcnow().isoformat(timespec='minutes')}\n")
    f.write("- Region: UK\n")
    f.write("- Status: Pipeline ran successfully\n\n")

# --------------------
# Google Trends
# --------------------
def fetch_uk_trends():
    pytrends = TrendReq(hl="en-GB", tz=0)
    trending = pytrends.trending_searches(pn="united_kingdom")
    trends = trending[0].tolist()
    return trends[:MAX_TRENDS]

def normalize_trends(trends):
    cleaned = []
    blacklist = [
        "news", "election", "politics", "war", "covid",
        "death", "killed", "court", "trial"
    ]

    for t in trends:
        t_clean = t.strip()
        if len(t_clean) < 3:
            continue
        if any(b in t_clean.lower() for b in blacklist):
            continue
        cleaned.append(t_clean)

    return cleaned

# --------------------
# Report
# --------------------
def write_trends_section(f, trends):
    f.write("## UK Google Trends (Filtered)\n\n")
    if not trends:
        f.write("_No usable trends today._\n\n")
        return

    for t in trends:
        f.write(f"- {t}\n")
    f.write("\n")

def write_next_steps(f):
    f.write("## Next Steps\n\n")
    f.write(
        "These trends should be evaluated for:\n"
        "- Small fidgets\n"
        "- Mini figurines\n"
        "- Desk toys\n"
        "- Blind-box suitability\n\n"
        "Next iteration will map these trends to MakerWorld models.\n"
    )

# --------------------
# Main
# --------------------
def main():
    ensure_reports_dir()
    path = report_path()

    trends_raw = fetch_uk_trends()
    trends = normalize_trends(trends_raw)

    with open(path, "w", encoding="utf-8") as f:
        write_header(f)
        write_trends_section(f, trends)
        write_next_steps(f)

    print(f"Report written to {path}")

if __name__ == "__main__":
    main()
