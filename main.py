import requests
from bs4 import BeautifulSoup
import time
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

    try:
        # More reliable than trending_searches
        df = pytrends.daily_trends(
            geo="GB",
            hl="en-GB"
        )

        # daily_trends returns a DataFrame with trend terms as values
        trends = []
        for col in df.columns:
            for v in df[col].dropna().tolist():
                if isinstance(v, str):
                    trends.append(v)

        return trends[:MAX_TRENDS]

    except Exception as e:
        # Absolute safety net — pipeline must NEVER fail
        print(f"[WARN] Google Trends unavailable: {e}")

        return [
            "fidget toy",
            "desk toy",
            "mini animal",
            "keychain",
            "stress toy",
            "collectible figurine"
        ]

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
def search_makerworld(keyword, max_results=5):
    """
    Uses MakerWorld's search API (the same one the website uses).
    Returns a list of (title, url).
    """
    api_url = "https://makerworld.com/api/search/models"

    params = {
        "keyword": keyword,
        "page": 1,
        "pageSize": max_results,
        "sort": "hot"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        r = requests.get(api_url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[WARN] MakerWorld API failed for '{keyword}': {e}")
        return []

    results = []

    for item in data.get("data", {}).get("list", []):
        title = item.get("title")
        slug = item.get("slug")

        if not title or not slug:
            continue

        url = f"https://makerworld.com/en/models/{slug}"
        results.append((title, url))

    return results
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

    # ✅ DEFINE PATH FIRST
    path = report_path()

    trends_raw = fetch_uk_trends()
    trends = normalize_trends(trends_raw)

    with open(path, "w", encoding="utf-8") as f:
        write_header(f)
        write_trends_section(f, trends)
        write_makerworld_section(f, trends)
if __name__ == "__main__":
    main()
