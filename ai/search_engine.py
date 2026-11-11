"""Search Engine — DuckDuckGo + StackOverflow"""
import httpx
import urllib.parse
from logger import get_logger

log = get_logger("ai.search")

async def search_web(query: str, max_results: int = 5, mock: bool = False) -> str:
    """بحث شامل"""
    if mock:
        return f"[Mock Search Results for: {query}]"

    results = []
    q = urllib.parse.quote(query)

    # DuckDuckGo
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1")
            if r.status_code == 200:
                d = r.json()
                if d.get("AbstractText"):
                    results.append(f"DuckDuckGo: {d['AbstractText'][:300]}")
                for t in (d.get("RelatedTopics") or [])[:3]:
                    if isinstance(t, dict) and t.get("Text"):
                        results.append(f"Info: {t['Text'][:200]}")
    except Exception as e:
        log.warning(f"DDG failed: {str(e)[:60]}")

    # Stack Overflow (لأسئلة البرمجة)
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={q}&site=stackoverflow&pagesize=3"
            r = await c.get(url)
            if r.status_code == 200:
                d = r.json()
                for item in (d.get("items") or [])[:3]:
                    results.append(f"StackOverflow: {item.get('title','')[:100]}")
    except Exception as e:
        log.warning(f"SO failed: {str(e)[:60]}")

    return "\n".join(results[:max_results]) if results else None
