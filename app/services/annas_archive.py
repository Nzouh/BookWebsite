import httpx
from selectolax.parser import HTMLParser
import urllib.parse
import re
import os
import json
from pathvalidate import sanitize_filename
import logging

logger = logging.getLogger(__name__)

ANNAS_SEARCH_ENDPOINT = "https://annas-archive.li/search?q={}"
ANNAS_DOWNLOAD_ENDPOINT = "https://annas-archive.li/dyn/api/fast_download.json?md5={}&key={}"

class Book:
    def __init__(self, language="", format="", size="", title="", publisher="", authors="", url="", hash="", cover_url="", cover_data=""):
        self.language = language
        self.format = format
        self.size = size
        self.title = title
        self.publisher = publisher
        self.authors = authors
        self.url = url
        self.hash = hash
        self.cover_url = cover_url
        self.cover_data = cover_data

    def to_dict(self):
        return vars(self)

    async def download(self, secret_key: str, folder_path: str):
        api_url = ANNAS_DOWNLOAD_ENDPOINT.format(self.hash, secret_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(api_url)
            if resp.status_code != 200:
                raise Exception(f"Failed to get download URL: HTTP {resp.status_code}")
            
            data = resp.json()
            download_url = data.get("download_url")
            if not download_url:
                err_msg = data.get("error", "failed to get download URL")
                raise Exception(err_msg)

            download_resp = await client.get(download_url, follow_redirects=True)
            if download_resp.status_code != 200:
                raise Exception("failed to download file")

            filename = f"{sanitize_filename(self.title)}.{self.format}"
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "wb") as f:
                f.write(download_resp.content)
            
            return file_path

def extract_meta_information(meta: str):
    if not meta:
        return "", "", ""
    
    parts = [p.strip() for p in meta.split("·")]
    language, format, size = "", "", ""

    for part in parts:
        if "[" in part and "]" in part:
            language = part
        
        upper = part.upper()
        if upper in ["PDF", "EPUB", "ZIP", "MOBI", "AZW3", "TXT", "DOC", "DOCX"]:
            format = part
            
        if any(unit in upper for unit in ["MB", "KB", "GB"]):
            size = part
            
    return language, format, size

async def find_books(query: str):
    full_url = ANNAS_SEARCH_ENDPOINT.format(urllib.parse.quote(query))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        resp = await client.get(full_url, follow_redirects=True)
        if resp.status_code != 200:
            return []

    parser = HTMLParser(resp.text)
    book_list = []
    seen_hashes = set()

    # The Go code looks for a[href*='/md5/'] and .js-vim-focus
    anchors = parser.css("a[href*='/md5/']")
    
    for a in anchors:
        href = a.attributes.get("href", "")
        if not href or "/md5/" not in href:
            continue
            
        book_hash = href.split("/md5/")[-1]
        if book_hash in seen_hashes:
            continue
        seen_hashes.add(book_hash)

        # Finding the main container (div.flex)
        container = a
        while container and "flex" not in (container.attributes.get("class") or ""):
            container = container.parent
            if not container: break
            
        if not container:
            continue

        title = a.text(strip=True)
        authors = ""
        
        # Author link is often next to title link
        author_link = a.next_sibling
        while author_link and author_link.tag != "a":
            author_link = author_link.next_sibling
            
        if author_link:
            authors = author_link.text(strip=True).replace("👤", "").strip()

        meta = ""
        # Look for the metadata line (contains dots and sizes)
        for div in container.css("div"):
            text = div.text(strip=True)
            if "·" in text and any(ext in text.upper() for ext in ["PDF", "EPUB", "MB", "KB"]):
                # Clean text like Go code (remove 'Save', '(function', etc)
                clean_text = text
                if "Save" in clean_text:
                    clean_text = clean_text.split("Save")[0].strip()
                if "(function" in clean_text:
                    clean_text = clean_text.split("(function")[0].strip()
                
                if len(clean_text) > 10:
                    meta = clean_text
                    break

        language, fmt, size = extract_meta_information(meta)
        
        # Cover logic
        cover_url = ""
        cover_data = ""
        
        cover_link = container.css_first("a.custom-a.block")
        if cover_link:
            img = cover_link.css_first("img")
            if img:
                src = img.attributes.get("src", "")
                if src:
                    cover_url = urllib.parse.urljoin(full_url, src) if not src.startswith("http") else src
            
            if not cover_url:
                fallback = cover_link.css_first("div.js-aarecord-list-fallback-cover")
                if fallback:
                    style = fallback.attributes.get("style", "")
                    title_div = fallback.css_first("div.font-bold.text-violet-900")
                    author_div = fallback.css_first("div.font-bold.text-amber-900")
                    cover_data = f"fallback:bg={style};title={title_div.text() if title_div else ''};author={author_div.text() if author_div else ''}"

        # Fallback image search
        if not cover_url:
            for img in container.css("img"):
                src = img.attributes.get("src", "")
                if src:
                    cover_url = urllib.parse.urljoin(full_url, src) if not src.startswith("http") else src
                    break

        book = Book(
            language=language.strip("[]()· "),
            format=fmt.strip("[]()· "),
            size=size.strip("[]()· "),
            title=title,
            authors=authors,
            url=urllib.parse.urljoin(full_url, href),
            hash=book_hash,
            cover_url=cover_url,
            cover_data=cover_data
        )
        book_list.append(book)

    return book_list

async def get_book_metadata(book_hash: str):
    books = await find_books(book_hash)
    for b in books:
        if b.hash == book_hash:
            return b
    return None
