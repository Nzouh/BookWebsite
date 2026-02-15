import asyncio
import sys
import os
sys.path.append(os.getcwd())
from app.services.annas_archive import AnnasArchiveService

async def verify():
    print("Verifying Anna's Archive Scraper...")
    service = AnnasArchiveService()
    
    query = "Harry Potter"
    print(f"Searching for: {query}")
    results = await service.search(query, limit=5)
    
    if not results:
        print("❌ No results found. Scraper might be blocked or selector is broken.")
        return

    print(f"✅ Found {len(results)} results.")
    first = results[0]
    print(f"  Title: {first.get('title')}")
    print(f"  MD5: {first.get('md5')}")
    print(f"  DL Link: {first.get('source_url')}")
    
    if first.get('md5'):
        print(f"Fetching download links for MD5: {first['md5']}...")
        links = await service.get_download_links(first['md5'])
        print(f"  Found {len(links)} download mirrors.")
        for l in links:
            print(f"    - {l['label']}: {l['url']}")

if __name__ == "__main__":
    asyncio.run(verify())
