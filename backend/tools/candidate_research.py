import os
import json

SCHEMA = {
    "name": "search_candidates",
    "description": "Search the web for job candidates matching a role and location. Returns LinkedIn profiles and professional directory results.",
    "input_schema": {
        "type": "object",
        "properties": {
            "role":        {"type": "string", "description": "Job title (e.g. 'Store Manager', 'Sales Associate')"},
            "location":    {"type": "string", "description": "City or country (e.g. 'Madrid', 'Amsterdam')"},
            "max_results": {"type": "integer", "description": "Max candidates to return (default 5)"},
        },
        "required": ["role", "location"],
    },
}


def search_candidates(role: str, location: str, max_results: int = 5) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "TAVILY_API_KEY not set",
            "hint": "Add your Tavily API key to enable candidate search. Free tier at tavily.com"
        })

    try:
        from tavily import TavilyClient
    except ImportError:
        return json.dumps({"error": "tavily-python not installed — run: pip install tavily-python"})

    client = TavilyClient(api_key=api_key)

    queries = [
        f'site:linkedin.com/in "{role}" "{location}"',
        f'"{role}" "{location}" candidate profile',
    ]

    seen_urls = set()
    candidates = []

    for query in queries:
        if len(candidates) >= max_results:
            break
        try:
            response = client.search(query, max_results=max_results, search_depth="basic")
            for r in response.get("results", []):
                url = r.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                candidates.append({
                    "name":        r.get("title", "Unknown"),
                    "summary":     r.get("content", "")[:250],
                    "profile_url": url,
                    "source":      "linkedin" if "linkedin.com" in url else "web",
                })
                if len(candidates) >= max_results:
                    break
        except Exception as e:
            candidates.append({"query": query, "error": str(e)})

    return json.dumps({
        "role":        role,
        "location":    location,
        "candidates":  candidates[:max_results],
        "total_found": len(candidates),
    }, indent=2)
