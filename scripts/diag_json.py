import httpx
from selectolax.parser import HTMLParser
import asyncio
import re

async def diagnostic():
    url = "https://annas-archive.li/search?q=Harry+Potter"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url, follow_redirects=True)
        
    # Look for any script that contains 'md5'
    scripts = re.findall(r'<script.*?> (.*?) </script>', resp.text, re.DOTALL | re.IGNORECASE)
    print(f"Found {len(scripts)} script tags")
    
    for i, s in enumerate(scripts):
        if "md5" in s:
            print(f"--- SCRIPT {i} (contains 'md5') ---")
            print(s[:500]) # Print first 500 chars

    # Also check if it's in a specific data attribute
    parser = HTMLParser(resp.text)
    for div in parser.css("div"):
        if div.attributes.get("data-search-results"):
            print("--- FOUND DATA-SEARCH-RESULTS ---")
            print(div.attributes.get("data-search-results")[:500])

if __name__ == "__main__":
    asyncio.run(diagnostic())
