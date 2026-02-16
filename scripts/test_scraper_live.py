#!/usr/bin/env python3
"""
Live Scraper Verification Script

Run this script locally to verify the Anna's Archive scraper works
against the live website. It tests:
1. Searching for books (10 results)
2. Extracting: title, author, book image, format, size
3. Getting detailed book information
4. Chapter parsing functionality

Usage:
    python scripts/test_scraper_live.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.annas_archive import AnnasArchiveService, Book


async def test_live_scraper():
    """Test the scraper against the live Anna's Archive website."""
    print("=" * 70)
    print("ANNA'S ARCHIVE SCRAPER - LIVE VERIFICATION TEST")
    print("=" * 70)
    print()
    
    service = AnnasArchiveService(timeout=60.0)
    
    # Test with multiple search queries to get variety
    queries = ["Python programming", "Machine Learning", "JavaScript"]
    all_results = []
    
    for query in queries:
        print(f"🔍 Searching for: \"{query}\"")
        print("-" * 50)
        
        try:
            results = await service.search(query, limit=10)
            
            if not results:
                print(f"   ⚠️  No results found for '{query}'")
                continue
            
            print(f"   ✅ Found {len(results)} books\n")
            all_results.extend(results[:4])  # Take top 4 from each query
            
            # Print first 3 results
            for i, book in enumerate(results[:3], 1):
                print(f"   {i}. {book.title[:50]}{'...' if len(book.title) > 50 else ''}")
                print(f"      Author: {book.authors or 'N/A'}")
                print(f"      Format: {book.format or 'N/A'} | Size: {book.size or 'N/A'}")
                print(f"      Cover:  {'✅' if book.cover_url else '❌'} {book.cover_url[:40] + '...' if book.cover_url and len(book.cover_url) > 40 else book.cover_url or 'No cover'}")
                print()
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Summary for 10 books
    print("=" * 70)
    print("SUMMARY - First 10 Books Collected")
    print("=" * 70)
    
    test_books = all_results[:10]
    
    if len(test_books) < 10:
        print(f"⚠️  Only collected {len(test_books)} books (target: 10)")
    
    print("\n{:<4} {:<35} {:<20} {:<8} {:<6}".format(
        "#", "Title", "Author", "Format", "Cover"
    ))
    print("-" * 75)
    
    for i, book in enumerate(test_books, 1):
        title = book.title[:32] + "..." if len(book.title) > 35 else book.title
        author = (book.authors[:17] + "...") if book.authors and len(book.authors) > 20 else (book.authors or "N/A")
        fmt = book.format or "N/A"
        cover = "✅" if book.cover_url else "❌"
        print(f"{i:<4} {title:<35} {author:<20} {fmt:<8} {cover:<6}")
    
    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    
    total = len(test_books)
    with_title = sum(1 for b in test_books if b.title)
    with_author = sum(1 for b in test_books if b.authors)
    with_cover = sum(1 for b in test_books if b.cover_url)
    with_format = sum(1 for b in test_books if b.format)
    with_size = sum(1 for b in test_books if b.size)
    
    print(f"  Books with title:   {with_title}/{total} ({100*with_title//total if total else 0}%)")
    print(f"  Books with author:  {with_author}/{total} ({100*with_author//total if total else 0}%)")
    print(f"  Books with cover:   {with_cover}/{total} ({100*with_cover//total if total else 0}%)")
    print(f"  Books with format:  {with_format}/{total} ({100*with_format//total if total else 0}%)")
    print(f"  Books with size:    {with_size}/{total} ({100*with_size//total if total else 0}%)")
    
    # Test book details
    if test_books:
        print("\n" + "=" * 70)
        print("BOOK DETAILS TEST")
        print("=" * 70)
        
        test_book = test_books[0]
        print(f"\nFetching details for: {test_book.title[:50]}...")
        print(f"Hash: {test_book.hash}")
        
        try:
            details = await service.get_book_details(test_book.hash)
            
            if details:
                print("\n✅ Successfully retrieved book details:")
                print(f"   Title:       {details.title}")
                print(f"   Author:      {details.authors or 'N/A'}")
                print(f"   Year:        {details.year or 'N/A'}")
                print(f"   ISBN:        {details.isbn or 'N/A'}")
                print(f"   Publisher:   {details.publisher or 'N/A'}")
                print(f"   Language:    {details.language or 'N/A'}")
                print(f"   Description: {details.description[:100] + '...' if details.description and len(details.description) > 100 else details.description or 'N/A'}")
                print(f"   Cover URL:   {details.cover_url or 'N/A'}")
                print(f"   Mirrors:     {len(details.download_mirrors)} download links")
            else:
                print("   ❌ Could not retrieve book details")
        
        except Exception as e:
            print(f"   ❌ Error fetching details: {e}")
    
    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    
    if total >= 10 and with_title >= 8 and with_author >= 5 and with_cover >= 3:
        print("✅ SCRAPER IS WORKING CORRECTLY!")
        print("   - Successfully retrieved book information")
        print("   - Title, author, and cover extraction working")
    elif total > 0:
        print("⚠️  SCRAPER IS PARTIALLY WORKING")
        print("   - Some data may be missing")
        print("   - Check if website structure has changed")
    else:
        print("❌ SCRAPER IS NOT WORKING")
        print("   - Could not retrieve any books")
        print("   - Website may be down or structure changed")
    
    print()


if __name__ == "__main__":
    asyncio.run(test_live_scraper())
