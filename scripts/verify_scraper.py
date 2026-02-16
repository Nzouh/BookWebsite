import asyncio
import sys
import os
sys.path.append(os.getcwd())
from app.services.annas_archive import AnnasArchiveService, Book

async def verify():
    print("=" * 60)
    print("Verifying Anna's Archive Scraper")
    print("=" * 60)
    
    service = AnnasArchiveService()
    
    # Test 1: Search functionality
    print("\n[Test 1] Search Functionality")
    print("-" * 40)
    query = "Harry Potter"
    print(f"Searching for: {query}")
    
    try:
        results = await service.search(query, limit=5)
        
        if not results:
            print("❌ No results found. Scraper might be blocked or selector is broken.")
            print("   (This could also be due to network restrictions)")
        else:
            print(f"✅ Found {len(results)} results.")
            first = results[0]
            print(f"\nFirst result:")
            print(f"  Title:  {first.title}")
            print(f"  Author: {first.authors}")
            print(f"  Format: {first.format}")
            print(f"  Size:   {first.size}")
            print(f"  Hash:   {first.hash}")
            print(f"  URL:    {first.url}")
            
            # Test 2: Get book details
            print("\n[Test 2] Get Book Details")
            print("-" * 40)
            if first.hash:
                print(f"Fetching details for MD5: {first.hash}")
                details = await service.get_book_details(first.hash)
                if details:
                    print(f"✅ Got book details:")
                    print(f"  Title:       {details.title}")
                    print(f"  Author:      {details.authors}")
                    print(f"  Description: {details.description[:100]}..." if details.description else "  Description: N/A")
                    print(f"  Year:        {details.year or 'N/A'}")
                    print(f"  Publisher:   {details.publisher or 'N/A'}")
                    print(f"  ISBN:        {details.isbn or 'N/A'}")
                else:
                    print("❌ Could not get book details")
            
            # Test 3: Get download links
            print("\n[Test 3] Get Download Links")
            print("-" * 40)
            if first.hash:
                print(f"Fetching download links for MD5: {first.hash}")
                links = await service.get_download_links(first.hash)
                print(f"  Found {len(links)} download mirrors:")
                for link in links[:5]:  # Show first 5
                    print(f"    - {link['label']}: {link['url'][:60]}...")
            
            # Test 4: Author biography (optional)
            print("\n[Test 4] Get Author Biography (Optional)")
            print("-" * 40)
            if first.authors:
                print(f"Searching for author info: {first.authors}")
                author_info = await service.get_author_biography(first.authors)
                if author_info and author_info.biography:
                    print(f"✅ Found author bio:")
                    print(f"  {author_info.biography[:200]}...")
                else:
                    print("ℹ️  No author biography found (this is optional)")
            
            # Test 5: Chapter parsing
            print("\n[Test 5] Chapter Parsing")
            print("-" * 40)
            sample_content = """
Chapter 1: The Beginning
This is the content of chapter 1.
It spans multiple lines.

Chapter 2: The Middle
This is chapter 2 content.
More text here.

Chapter 3: The End
Final chapter content.
"""
            chapters = service.parse_book_content_to_chapters(sample_content)
            print(f"✅ Parsed {len(chapters)} chapters from sample text:")
            for ch in chapters:
                print(f"  [{ch.order}] {ch.title}: {len(ch.content)} chars")
                
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Verification Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify())
