import httpx
from selectolax.parser import HTMLParser
import asyncio

async def diagnostic():
    url = "https://annas-archive.li/search?q=Harry+Potter"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url, follow_redirects=True)
        print(f"Status: {resp.status_code}")
        
    parser = HTMLParser(resp.text)
    anchors = parser.css("a[href*='/md5/']")
    print(f"Found {len(anchors)} anchors")
    
    if anchors:
        first = anchors[0]
        print("--- FIRST ANCHOR HTML ---")
        print(first.html[:1000])
        print("--- FIRST ANCHOR TEXT ---")
        print(f"'.text()': '{first.text(strip=True)}'")
        print("--- PARENT TEXT ---")
        print(first.parent.text(strip=True))

if __name__ == "__main__":
    asyncio.run(diagnostic())
