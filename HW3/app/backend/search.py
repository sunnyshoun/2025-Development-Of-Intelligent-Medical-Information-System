import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

async def fetch(session, url, headers=None):
    async with session.get(url, headers=headers) as response:
        if response.content_type == "application/json":
            return await response.json(content_type=None)
        return await response.text()

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
        return [{"title": item["title"], "link": item["href"], "source": "DuckDuckGo"} for item in results]

async def search_yahoo(query):
    url = f"https://search.yahoo.com/search?p={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url, headers)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for item in soup.select('.algo .compTitle a')[:10]:
            title = item.get_text()
            link = item.get('href')
            if title and link:
                results.append({"title": title, "link": link, "source": "Yahoo"})
        
        return results
    
async def search_bing(query):
    url = f"https://www.bing.com/search?q={query}&count=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url, headers)
        if not html:
            print("Bing: Failed to fetch HTML")
            return []
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        search_items = soup.select('.b_algo a, .b_algo h2 a, .b_title a')[:10]
        
        for item in search_items:
            title = item.get_text(strip=True)
            link = item.get('href')
            if title and link:
                results.append({"title": title, "link": link, "source": "Bing"})
        
        return results

async def search_meta(query):
    google_results = await search_google(query)
    loop = asyncio.get_event_loop()
    duckduckgo_results = await loop.run_in_executor(None, search_duckduckgo, query)
    yahoo_results = await search_yahoo(query)
    bing_results = await search_bing(query)
    
    results = []
    if isinstance(google_results, list):
        results.extend(google_results)
    else:
        print("Google Search Failed:", google_results)
    if isinstance(duckduckgo_results, list):
        results.extend(duckduckgo_results)
    else:
        print("DuckDuckGo Search Failed:", duckduckgo_results)
    if isinstance(yahoo_results, list):
        results.extend(yahoo_results)
    else:
        print("Yahoo Search Failed:", yahoo_results)
    if isinstance(bing_results, list):
        results.extend(bing_results)
    else:
        print("Bing Search Failed:", bing_results)
    
    return results

if __name__ == "__main__":
    query = "川普"
    results = asyncio.run(search_meta(query))
    print("Final Results:", results)