import os
import httpx
import json


APIFY_ACTORS = {
    "linkedin": "hKByXkMQaC5Qt9UMN",
    "indeed":   "MXLpngmVpE8WTESQr",
    "glassdoor": "5OaooRg0FxlRF0L1B",
}


def search_candidates(role: str, location: str, max_results: int = 10) -> str:
    api_key = os.getenv("APIFY_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "APIFY_API_KEY not set in .env",
            "hint": "Add your Apify API key to .env to enable live candidate search"
        })

    results = []
    for source, actor_id in APIFY_ACTORS.items():
        try:
            url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
            payload = {"searchQuery": role, "location": location, "maxItems": max_results // 3}
            resp = httpx.post(url, params={"token": api_key}, json=payload, timeout=60)
            resp.raise_for_status()
            items = resp.json()
            for item in items[:max_results // 3]:
                results.append({
                    "source": source,
                    "name": item.get("fullName") or item.get("name", "N/A"),
                    "title": item.get("headline") or item.get("jobTitle", "N/A"),
                    "location": item.get("location", location),
                    "profile_url": item.get("linkedInUrl") or item.get("url", ""),
                })
        except Exception as e:
            results.append({"source": source, "error": str(e)})

    return json.dumps({"role": role, "location": location, "candidates": results}, indent=2)
