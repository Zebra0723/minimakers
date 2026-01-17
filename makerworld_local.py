import requests
import time

MAX_MODELS = 5

def search_makerworld(keyword):
    url = "https://makerworld.com/api/search/models"

    params = {
        "keyword": keyword,
        "page": 1,
        "pageSize": MAX_MODELS,
        "sort": "hot"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()

    data = r.json()
    results = []

    for item in data.get("data", {}).get("list", []):
        title = item.get("title")
        slug = item.get("slug")

        if title and slug:
            url = f"https://makerworld.com/en/models/{slug}"
            results.append((title, url))

    return results


def run():
    keywords = [
        "fidget toy",
        "desk toy",
        "mini animal",
        "keychain",
        "stress toy",
        "collectible figurine"
    ]

    print("\n=== MakerWorld Model Candidates ===\n")

    for kw in keywords:
        print(f"\n🔍 {kw}")
        models = search_makerworld(kw)

        if not models:
            print("  (no results)")
            continue

        for title, url in models:
            print(f"  - {title}")
            print(f"    {url}")

        time.sleep(1)


if __name__ == "__main__":
    run()
