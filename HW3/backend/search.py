import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

async def fetch(session, url, headers=None):
    async with session.get(url, headers=headers) as response:
        return await response.json(content_type=None)

async def search_google(query):
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        print("Error: GOOGLE_API_KEY or GOOGLE_CX is not set.")
        return []
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        if "error" in data:
            print("Google API Error:", data["error"])
            return []
        return [{"title": item["title"], "link": item["link"], "source": "Google"} for item in data.get("items", [])]

def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = ddgs.text(keywords=query, max_results=10)
        print("DuckDuckGo API Response:", results)
        return [{"title": item["title"], "link": item["href"], "source": "DuckDuckGo"} for item in results]

async def search_meta(query):
    google_results = await search_google(query)
    loop = asyncio.get_event_loop()
    duckduckgo_results = await loop.run_in_executor(None, search_duckduckgo, query)
    
    results = []
    if isinstance(google_results, list):
        results.extend(google_results)
    else:
        print("Google Search Failed:", google_results)
    if isinstance(duckduckgo_results, list):
        results.extend(duckduckgo_results)
    else:
        print("DuckDuckGo Search Failed:", duckduckgo_results)
    
    return results

if __name__ == "__main__":
    query = "川普"
    results = asyncio.run(search_meta(query))
    print("Final Results:", results)