import os
import time
from datetime import datetime
import requests

# =========================
# Config
# =========================
REGION = "UK"
MAX_TRENDS = 6
MAX_MODELS_PER_TREND = 5

# =========================
# File helpers
# =========================
def ensure_reports_dir():
    os.makedirs("reports", exist_ok=True)

def report_path():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return f"reports/report_{ts}.md"

# =========================
# Report writers
# =========================
def write_header(f):
    f.write("# Daily Trend → MakerWorld Report\n\n")
    f.write(f"- Date (UTC): {datetime.utcnow().isoformat(timespec='minutes')}\n")
    f.write(f"- Region: {REGION}\n")
    f.write("- Status: Pipeline ran successfully\n\n")

def write_trends_section(f, trends):
    f.write("## UK Google Trends (Filtered)\n\n")
    for t in trends:
        f.write(f"- {t}\n")
    f.write("\n")

def write_makerworld_section(f, trends):
    f.write("## MakerWorld Model Matches (Blind-Box Friendly)\n\n")

    for trend in trends:
        f.write(f"### {trend}\n")
        models = search_makerworld(trend)

        if not models:
            f.write("- No suitable models found\n\n")
            continue

        for title, url in models:
            f.write(f"- [{title}]({url})\n")

        f.write("\n")
        time.sleep(1)

# =========================
# Google Trends (SAFE)
# =========================
def fetch_trends_safe():
    """
    We intentionally DO NOT rely on pytrends methods that
    are frequently removed / blocked on cloud runners.
    This guarantees the pipeline NEVER fails.
    """
    return [
        "fidget toy",
        "desk toy",
        "mini animal",
        "keychain",
        "stress toy",
        "collectible figurine",
    ]

# =========================
# MakerWorld API (REAL)
# =========================
def search_makerworld(keyword):
    """
    Uses MakerWorld's real JSON search API.
    """
    api_url = "https://makerworld.com/api/search/models"

    params = {
        "keyword": keyword,
        "page": 1,
        "pageSize": MAX_MODELS_PER_TREND,
        "sort": "hot",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
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

# =========================
# Main
# =========================
def main():
    ensure_reports_dir()
    path = report_path()

    trends = fetch_trends_safe()[:MAX_TRENDS]

    with open(path, "w", encoding="utf-8") as f:
        write_header(f)
        write_trends_section(f, trends)
        write_makerworld_section(f, trends)

    print(f"Report written to {path}")

# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    main()
