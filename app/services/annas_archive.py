import httpx
from selectolax.parser import HTMLParser
import urllib.parse
import re
import os
import json
from pathvalidate import sanitize_filename
import logging
from typing import Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

# Configuration constants
BASE_URL = "https://annas-archive.li"
ANNAS_SEARCH_ENDPOINT = f"{BASE_URL}/search?q={{}}"
ANNAS_BOOK_DETAIL_ENDPOINT = f"{BASE_URL}/md5/{{}}"
ANNAS_DOWNLOAD_ENDPOINT = f"{BASE_URL}/dyn/api/fast_download.json?md5={{}}&key={{}}"

# Standard headers to avoid bot detection
# NOTE: Do NOT include "Accept-Encoding: br" (Brotli) unless the 'brotli'
# package is installed. httpx handles gzip/deflate natively.
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


@dataclass
class Chapter:
    """Represents a chapter extracted from a book."""
    title: str
    content: str
    order: int


@dataclass
class AuthorInfo:
    """Represents author information scraped from Anna's Archive."""
    name: str
    biography: Optional[str] = None
    profile_url: Optional[str] = None


@dataclass
class Book:
    """Represents a book scraped from Anna's Archive."""
    title: str = ""
    authors: str = ""
    language: str = ""
    format: str = ""
    size: str = ""
    publisher: str = ""
    year: str = ""
    isbn: str = ""
    description: str = ""
    url: str = ""
    hash: str = ""
    cover_url: str = ""
    cover_data: str = ""
    chapters: list = field(default_factory=list)
    author_biography: Optional[str] = None
    download_mirrors: list = field(default_factory=list)

    def to_dict(self):
        """Convert Book to dictionary."""
        return asdict(self)

    async def download(self, secret_key: str, folder_path: str) -> str:
        """
        Download the book file using the Anna's Archive fast download API.
        
        Args:
            secret_key: API key for fast download
            folder_path: Directory to save the downloaded file
            
        Returns:
            Path to the downloaded file
        """
        api_url = ANNAS_DOWNLOAD_ENDPOINT.format(self.hash, secret_key)
        
        async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=60.0) as client:
            resp = await client.get(api_url)
            if resp.status_code != 200:
                raise Exception(f"Failed to get download URL: HTTP {resp.status_code}")
            
            data = resp.json()
            download_url = data.get("download_url")
            if not download_url:
                err_msg = data.get("error", "Failed to get download URL")
                raise Exception(err_msg)

            download_resp = await client.get(download_url, follow_redirects=True, timeout=300.0)
            if download_resp.status_code != 200:
                raise Exception(f"Failed to download file: HTTP {download_resp.status_code}")

            # Create safe filename
            safe_title = sanitize_filename(self.title) if self.title else self.hash
            ext = self.format.lower() if self.format else "bin"
            filename = f"{safe_title}.{ext}"
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "wb") as f:
                f.write(download_resp.content)
            
            return file_path


def _extract_meta_information(meta: str) -> tuple[str, str, str]:
    """
    Extract language, format, and size from metadata string.
    
    Args:
        meta: Raw metadata string like "[en] · PDF · 2.5 MB"
        
    Returns:
        Tuple of (language, format, size)
    """
    if not meta:
        return "", "", ""
    
    parts = [p.strip() for p in meta.split("·")]
    language, fmt, size = "", "", ""

    for part in parts:
        part_clean = part.strip()
        
        # Check for language codes in brackets
        if "[" in part_clean and "]" in part_clean:
            language = part_clean
            continue
        
        # Check for file formats
        upper = part_clean.upper()
        known_formats = ["PDF", "EPUB", "ZIP", "MOBI", "AZW3", "TXT", "DOC", "DOCX", "CBR", "CBZ", "DJVU", "FB2"]
        if upper in known_formats:
            fmt = part_clean
            continue
            
        # Check for file sizes (check longer units first to avoid false positives)
        if any(unit in upper for unit in ["MB", "KB", "GB"]):
            size = part_clean
            
    return language, fmt, size


def _clean_text(text: str) -> str:
    """Clean scraped text by removing unwanted elements."""
    if not text:
        return ""
    
    # Remove common artifacts
    clean = text
    for artifact in ["Save", "(function", "undefined", "null"]:
        if artifact in clean:
            clean = clean.split(artifact)[0]
    
    # Clean whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def _clean_language(lang: str) -> str:
    """Clean language field: remove emoji prefixes and normalize."""
    if not lang:
        return ""
    # Remove common emoji prefixes (✅, 🗸, etc.)
    clean = re.sub(r'^[\U00002700-\U000027BF\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U00002600-\U000026FF\U00002702-\U000027B0\u2705\u2611\u2714]+\s*', '', lang)
    # Extract just "English [en]" pattern
    m = re.match(r'([A-Za-z\s]+(?:\[[a-z]{2,3}\])?)', clean.strip())
    if m:
        return m.group(1).strip()
    return clean.strip()


def _find_parent_with_class(element, class_pattern: str, max_depth: int = 10):
    """Find parent element containing a specific class pattern."""
    current = element
    depth = 0
    while current and depth < max_depth:
        class_attr = (current.attributes.get("class", "") or "") if hasattr(current, 'attributes') else ""
        if class_attr and class_pattern in class_attr:
            return current
        current = current.parent
        depth += 1
    return None


class AnnasArchiveService:
    """
    Service for scraping book information from Anna's Archive.
    
    Provides methods to:
    - Search for books
    - Get detailed book information
    - Extract author information
    - Get download links
    - Parse book content into chapters
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize the service.
        
        Args:
            timeout: Default request timeout in seconds
        """
        self.timeout = timeout
        self.headers = DEFAULT_HEADERS.copy()
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page and return its HTML content.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if request failed
        """
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                resp = await client.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    return resp.text
                logger.warning(f"Failed to fetch {url}: HTTP {resp.status_code}")
                return None
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def search(self, query: str, limit: int = 20) -> list[Book]:
        """
        Search for books on Anna's Archive.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of Book objects
        """
        full_url = ANNAS_SEARCH_ENDPOINT.format(urllib.parse.quote(query))
        html = await self._fetch_page(full_url)
        
        if not html:
            return []
        
        return self._parse_search_results(html, full_url, limit)
    
    def _parse_search_results(self, html: str, base_url: str, limit: int) -> list[Book]:
        """Parse search results HTML into Book objects."""
        parser = HTMLParser(html)
        book_list = []
        seen_hashes = set()

        # Each result lives in a container div inside js-aarecord-list-outer.
        # Structure per result:
        #   <div class="flex pt-3 pb-3 border-b ...">
        #     <a href="/md5/HASH">  ← cover image link (no visible text)
        #     <div>                  ← info column
        #       <a href="/md5/HASH"> ← title link (text-lg font-semibold)
        #       <a href="/search?q=Author"> ← author link with icon-[mdi--user-edit]
        #       <div class="text-gray-800 ..."> ← metadata: lang · fmt · size · ...
        result_containers = parser.css(
            "div.js-aarecord-list-outer > div.flex"
        )

        # Fallback: if the outer wrapper class changed, try the known inner pattern
        if not result_containers:
            result_containers = parser.css(
                "div.flex.pt-3.pb-3.border-b"
            )

        for container in result_containers:
            if len(book_list) >= limit:
                break

            # --- hash / URL ---
            first_md5_link = container.css_first("a[href*='/md5/']")
            if not first_md5_link:
                continue
            href = first_md5_link.attributes.get("href", "")
            book_hash = href.split("/md5/")[-1].split("?")[0].split("#")[0]
            if not book_hash or book_hash in seen_hashes:
                continue
            seen_hashes.add(book_hash)

            # --- title ---
            # The title is in the *second* /md5/ anchor which carries visible text
            title = ""
            md5_links = container.css("a[href*='/md5/']")
            for link in md5_links:
                text = link.text(strip=True)
                if text:
                    title = _clean_text(text)
                    break
            # Fallback: title stored in data-content on fallback cover div
            if not title:
                fb = container.css_first("div.font-bold[data-content]")
                if fb:
                    title = fb.attributes.get("data-content", "")

            # --- author ---
            authors = ""
            # Author link contains an icon span with class icon-[mdi--user-edit]
            author_icon = container.css_first("span[class*='icon-[mdi--user-edit]']")
            if author_icon and author_icon.parent:
                author_link = author_icon.parent
                authors = _clean_text(
                    author_link.text(strip=True).replace("\U0001f464", "")
                )
            # Fallback: second data-content div (amber author name)
            if not authors:
                dcs = container.css("div[data-content]")
                for dc in dcs:
                    cls = dc.attributes.get("class", "")
                    if "amber" in cls:
                        authors = dc.attributes.get("data-content", "")
                        break

            # --- metadata (language · format · size) ---
            meta = ""
            meta_div = container.css_first(
                "div.text-gray-800, div.text-sm.font-semibold"
            )
            if meta_div:
                # Re-parse the meta div HTML to strip <script> tags
                # without mutating the original tree
                meta_copy = HTMLParser(meta_div.html)
                for script in meta_copy.css("script"):
                    script.decompose()
                meta = meta_copy.text(strip=True)
                # Strip trailing "Save" button text
                if "Save" in meta:
                    meta = meta.split("Save")[0].strip().rstrip("·").strip()
            language, fmt, size = _extract_meta_information(meta)

            # --- year ---
            year = ""
            year_match = re.search(r'\b(19|20)\d{2}\b', meta)
            if year_match:
                year = year_match.group()

            # --- cover image ---
            cover_url = ""
            cover_data = ""
            img = container.css_first("img")
            if img:
                # Try src first, then data-src (lazy-loaded images)
                src = img.attributes.get("src", "")
                if not src or src.startswith("data:"):
                    src = img.attributes.get("data-src", "")
                if src and not src.startswith("data:"):
                    cover_url = (
                        urllib.parse.urljoin(base_url, src)
                        if not src.startswith("http")
                        else src
                    )

            book = Book(
                language=_clean_language(language),
                format=fmt.strip("[]()· "),
                size=size.strip("[]()· "),
                title=title,
                authors=authors,
                url=urllib.parse.urljoin(base_url, href),
                hash=book_hash,
                cover_url=cover_url,
                cover_data=cover_data,
                year=year,
            )
            book_list.append(book)

        return book_list
    
    def _extract_author_from_container(self, title_anchor, container) -> str:
        """Extract author name from the search result container."""
        authors = ""
        
        # Strategy 1: Look for author link next to title
        if title_anchor:
            sibling = title_anchor.next
            while sibling:
                if hasattr(sibling, 'tag') and sibling.tag == "a":
                    text = sibling.text(strip=True)
                    # Check if this looks like an author (not another book link)
                    if text and "/md5/" not in (sibling.attributes.get("href", "")):
                        authors = _clean_text(text.replace("👤", "").strip())
                        break
                sibling = getattr(sibling, 'next', None)
        
        # Strategy 2: Look for italic text (common for authors)
        if not authors and container:
            italic = container.css_first("i, em, .italic")
            if italic:
                text = italic.text(strip=True)
                if text and len(text) < 200:  # Reasonable author name length
                    authors = _clean_text(text.replace("👤", ""))
        
        # Strategy 3: Look for elements with specific author indicators
        if not authors and container:
            for elem in container.css("span, div"):
                text = elem.text(strip=True)
                if "👤" in text or "by " in text.lower():
                    authors = _clean_text(text.replace("👤", "").replace("by ", "").replace("By ", ""))
                    break
        
        return authors
    
    def _extract_metadata_from_container(self, container) -> str:
        """Extract metadata string from container."""
        if not container:
            return ""
        
        # Look for leaf divs/spans containing format/size info
        # Iterate through children to find metadata-like text
        for child in container.iter():
            if not hasattr(child, 'tag') or child.tag not in ['div', 'span', 'p']:
                continue
            
            text = child.text(strip=True)
            if not text:
                continue
                
            # Check for typical metadata patterns - must have separator
            if "·" not in text:
                continue
                
            # Verify it contains format/size indicators
            text_upper = text.upper()
            has_format = any(fmt in text_upper for fmt in ["PDF", "EPUB", "MOBI", "AZW3", "TXT", "DOC", "DOCX", "CBR", "CBZ", "DJVU", "FB2", "ZIP"])
            has_size = any(unit in text_upper for unit in ["MB", "KB", "GB"])
            
            if not (has_format or has_size):
                continue
            
            # Extract only the metadata portion (language · format · size)
            parts = text.split("·")
            meta_parts = []
            for part in parts:
                part = part.strip()
                part_upper = part.upper()
                is_language = "[" in part and "]" in part
                is_format = any(fmt in part_upper for fmt in ["PDF", "EPUB", "MOBI", "AZW3", "TXT", "DOC", "DOCX", "CBR", "CBZ", "DJVU", "FB2", "ZIP"])
                is_size = any(unit in part_upper for unit in ["MB", "KB", "GB"]) and any(c.isdigit() for c in part)
                
                if is_language or is_format or is_size:
                    meta_parts.append(part)
            
            if meta_parts:
                return " · ".join(meta_parts)
        
        return ""
    
    def _extract_cover_from_container(self, container, base_url: str) -> tuple[str, str]:
        """Extract cover image URL from container."""
        cover_url = ""
        cover_data = ""
        
        if not container:
            return cover_url, cover_data
        
        # Strategy 1: Look for img element
        for img in container.css("img"):
            src = img.attributes.get("src", "")
            if src and not src.startswith("data:"):
                cover_url = urllib.parse.urljoin(base_url, src) if not src.startswith("http") else src
                break
        
        # Strategy 2: Look for fallback cover div
        if not cover_url:
            fallback = container.css_first("div[class*='fallback'], div[class*='cover']")
            if fallback:
                style = fallback.attributes.get("style", "")
                title_div = fallback.css_first("div.font-bold")
                cover_data = f"fallback:bg={style};title={title_div.text() if title_div else ''}"
        
        return cover_url, cover_data
    
    async def get_book_details(self, md5_hash: str) -> Optional[Book]:
        """
        Get detailed information about a specific book.
        
        Args:
            md5_hash: The MD5 hash identifier of the book
            
        Returns:
            Book object with detailed information or None if not found
        """
        url = ANNAS_BOOK_DETAIL_ENDPOINT.format(md5_hash)
        html = await self._fetch_page(url)
        
        if not html:
            return None
        
        return self._parse_book_detail(html, url, md5_hash)
    
    def _parse_book_detail(self, html: str, base_url: str, md5_hash: str) -> Optional[Book]:
        """Parse book detail page HTML into a Book object."""
        parser = HTMLParser(html)
        
        book = Book(hash=md5_hash, url=base_url)
        
        # Extract title - multiple strategies
        # Strategy 1: Look for main heading
        title_elem = parser.css_first("h1, h2.text-3xl, h2.text-2xl, .text-3xl")
        if title_elem:
            book.title = _clean_text(title_elem.text(strip=True))
        
        # Strategy 2: Look in page title
        if not book.title:
            page_title = parser.css_first("title")
            if page_title:
                title_text = page_title.text(strip=True)
                # Remove site name suffix
                book.title = title_text.split(" - Anna")[0].strip()
        
        # Extract author
        book.authors = self._extract_author_from_detail(parser)
        
        # Extract description/biography
        book.description = self._extract_description_from_detail(parser)
        
        # Extract additional metadata
        self._extract_additional_metadata(parser, book)
        
        # Extract cover image
        book.cover_url = self._extract_cover_from_detail(parser, base_url)
        
        # Extract download mirrors
        book.download_mirrors = self._extract_download_mirrors(parser, base_url)
        
        return book
    
    def _extract_author_from_detail(self, parser: HTMLParser) -> str:
        """Extract author name from book detail page."""
        # Strategy 1: Look for author in metadata table/list
        for row in parser.css("tr, div.flex"):
            text = row.text(strip=True)
            lower_text = text.lower()
            if "author" in lower_text or "creator" in lower_text:
                # Get the value part
                parts = text.split(":")
                if len(parts) > 1:
                    return _clean_text(parts[1])
                # Try to find link or value element
                value_elem = row.css_first("a, td:last-child, span")
                if value_elem:
                    return _clean_text(value_elem.text(strip=True))
        
        # Strategy 2: Look for italic element near title (common pattern)
        italic = parser.css_first("h1 + div i, h1 + i, h2 + i, .italic")
        if italic:
            author_text = italic.text(strip=True)
            if author_text and len(author_text) < 200:
                return _clean_text(author_text.replace("by ", "").replace("By ", ""))
        
        # Strategy 3: Look for specific author link patterns
        for a in parser.css("a"):
            href = a.attributes.get("href", "")
            if "/author/" in href or "author=" in href:
                return _clean_text(a.text(strip=True))
        
        return ""
    
    def _extract_description_from_detail(self, parser: HTMLParser) -> str:
        """Extract book description from detail page."""
        # Strategy 1: Look for description in labeled sections
        for elem in parser.css("div, p"):
            class_attr = elem.attributes.get("class", "") or ""
            if "description" in class_attr.lower():
                return _clean_text(elem.text(strip=True))
        
        # Strategy 2: Look for long paragraphs that might be descriptions
        for p in parser.css("p"):
            text = p.text(strip=True)
            if len(text) > 100 and len(text) < 5000:
                # Check it's not just metadata
                if not any(x in text.lower() for x in ["isbn", "pages:", "publisher:"]):
                    return _clean_text(text)
        
        return ""
    
    def _extract_additional_metadata(self, parser: HTMLParser, book: Book):
        """Extract additional metadata like ISBN, year, publisher."""
        for row in parser.css("tr, div.flex, dl"):
            text = row.text(strip=True).lower()
            full_text = row.text(strip=True)
            
            if "isbn" in text:
                isbn_match = re.search(r'[\d-]{10,}', full_text)
                if isbn_match:
                    book.isbn = isbn_match.group()
            
            if "year" in text or "published" in text:
                year_match = re.search(r'\b(19|20)\d{2}\b', full_text)
                if year_match:
                    book.year = year_match.group()
            
            if "publisher" in text:
                parts = full_text.split(":")
                if len(parts) > 1:
                    book.publisher = _clean_text(parts[1])
            
            if "language" in text:
                parts = full_text.split(":")
                if len(parts) > 1 and not book.language:
                    book.language = _clean_text(parts[1])
    
    def _extract_cover_from_detail(self, parser: HTMLParser, base_url: str) -> str:
        """Extract cover image URL from detail page."""
        # Look for cover image
        for img in parser.css("img"):
            src = img.attributes.get("src", "") or ""
            alt = (img.attributes.get("alt", "") or "").lower()
            class_attr = (img.attributes.get("class", "") or "").lower()
            
            # Check if this looks like a cover image
            if src and ("cover" in alt or "cover" in class_attr or "book" in alt):
                return urllib.parse.urljoin(base_url, src) if not src.startswith("http") else src
        
        # Fallback: first reasonably sized image
        for img in parser.css("img"):
            src = img.attributes.get("src", "") or ""
            if src and not src.startswith("data:") and "icon" not in src.lower():
                return urllib.parse.urljoin(base_url, src) if not src.startswith("http") else src
        
        return ""
    
    def _extract_download_mirrors(self, parser: HTMLParser, base_url: str) -> list[dict]:
        """Extract download mirror links from detail page."""
        mirrors = []
        
        # Look for download links
        for a in parser.css("a"):
            href = a.attributes.get("href", "")
            text = a.text(strip=True)
            
            # Check for download-related links
            if any(kw in href.lower() for kw in ["download", "slow_download", "fast_download", "libgen", "ipfs", "z-library"]):
                label = text if text else "Download"
                full_url = urllib.parse.urljoin(base_url, href) if not href.startswith("http") else href
                mirrors.append({"label": label, "url": full_url})
        
        return mirrors
    
    async def get_download_links(self, md5_hash: str) -> list[dict]:
        """
        Get download links for a book.
        
        Args:
            md5_hash: The MD5 hash identifier of the book
            
        Returns:
            List of dictionaries with 'label' and 'url' keys
        """
        book = await self.get_book_details(md5_hash)
        if book:
            return book.download_mirrors
        return []
    
    async def get_author_biography(self, author_name: str) -> Optional[AuthorInfo]:
        """
        Try to get author biography information.
        
        This searches for the author and attempts to extract biographical info
        from book descriptions and author pages.
        
        Args:
            author_name: Name of the author
            
        Returns:
            AuthorInfo object or None if not found
        """
        if not author_name:
            return None
        
        # Search for books by this author to find biographical info
        search_results = await self.search(f'author:"{author_name}"', limit=5)
        
        biography = None
        for book in search_results:
            if book.authors and author_name.lower() in book.authors.lower():
                # Get detailed info which might include author bio
                details = await self.get_book_details(book.hash)
                if details and details.description:
                    # Check if description contains author info
                    desc_lower = details.description.lower()
                    if "author" in desc_lower or "biography" in desc_lower or "about" in desc_lower:
                        biography = details.description
                        break
        
        return AuthorInfo(
            name=author_name,
            biography=biography
        )
    
    def parse_book_content_to_chapters(self, content: str, format_type: str = "txt") -> list[Chapter]:
        """
        Parse book content into chapters.
        
        This method attempts to identify chapter boundaries in book content
        and split them into separate Chapter objects.
        
        Args:
            content: The raw text content of the book
            format_type: The format of the content (txt, etc.)
            
        Returns:
            List of Chapter objects
        """
        if not content:
            return []
        
        chapters = []
        
        # Common chapter patterns with named groups for better extraction
        # Each tuple: (pattern, prefix for title)
        # Roman numeral pattern: valid sequences that must contain at least one character
        # This pattern requires at least one Roman numeral character (I, V, X, L, C, D, or M)
        roman_pattern = r'(?:M{1,3}|(?:CM|CD|D?C{1,3})|(?:XC|XL|L?X{1,3})|(?:IX|IV|V?I{1,3}))'
        chapter_patterns = [
            # Chapter with number or roman numeral
            (rf'^(?:Chapter|CHAPTER)\s+(\d+|{roman_pattern})[\s:.]+(.*)$', 'Chapter'),
            (rf'^(?:Chapter|CHAPTER)\s+(\d+|{roman_pattern})$', 'Chapter'),  # Chapter without title
            # Part with number or roman numeral  
            (rf'^(?:PART|Part)\s+(\d+|{roman_pattern})[\s:.]+(.*)$', 'Part'),
            (rf'^(?:PART|Part)\s+(\d+|{roman_pattern})$', 'Part'),  # Part without title
            # Section with number
            (r'^(?:Section|SECTION)\s+(\d+)[\s:.]+(.*)$', 'Section'),
            (r'^(?:Section|SECTION)\s+(\d+)$', 'Section'),
            # Numbered chapters like "1. Title" - title can be any text starting with capital
            (r'^(\d+)\.\s+([A-Z].*)$', 'Chapter'),
        ]
        
        # Try to split by chapter markers
        lines = content.split('\n')
        current_chapter_title = None  # None means no chapter started yet
        current_chapter_content = []
        chapter_order = 0
        found_any_chapter = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line is a chapter header
            is_chapter_header = False
            for pattern, prefix in chapter_patterns:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    found_any_chapter = True
                    
                    # Save previous chapter if we have a title (even with empty content)
                    if current_chapter_title is not None:
                        chapters.append(Chapter(
                            title=current_chapter_title,
                            content='\n'.join(current_chapter_content).strip(),
                            order=chapter_order
                        ))
                        chapter_order += 1
                    
                    # Start new chapter
                    groups = match.groups()
                    chapter_num = groups[0] if groups else ""
                    chapter_title_part = groups[1].strip() if len(groups) > 1 and groups[1] else ""
                    
                    if chapter_title_part:
                        current_chapter_title = f"{prefix} {chapter_num}: {chapter_title_part}"
                    else:
                        current_chapter_title = f"{prefix} {chapter_num}"
                    
                    current_chapter_content = []
                    is_chapter_header = True
                    break
            
            if not is_chapter_header:
                # If we haven't found any chapter headers yet, this is intro content
                if current_chapter_title is None and not found_any_chapter:
                    if line_stripped:  # Only add non-empty lines to potential intro
                        current_chapter_content.append(line)
                elif current_chapter_title is not None:
                    current_chapter_content.append(line)
        
        # Don't forget the last chapter
        if current_chapter_title is not None:
            chapters.append(Chapter(
                title=current_chapter_title,
                content='\n'.join(current_chapter_content).strip(),
                order=chapter_order
            ))
        
        # If there was intro content before any chapters, add it as Introduction
        # (This case is handled by having intro content collected before first chapter)
        
        # If no chapters were found, treat entire content as single chapter
        if not chapters:
            chapters.append(Chapter(
                title="Full Text",
                content=content.strip(),
                order=0
            ))
        
        return chapters


# Backward compatibility functions
async def find_books(query: str) -> list[Book]:
    """
    Search for books on Anna's Archive.
    
    This is a backward-compatible wrapper around AnnasArchiveService.search().
    """
    service = AnnasArchiveService()
    return await service.search(query)


async def get_book_metadata(book_hash: str) -> Optional[Book]:
    """
    Get metadata for a specific book.
    
    This is a backward-compatible wrapper around AnnasArchiveService.get_book_details().
    """
    service = AnnasArchiveService()
    return await service.get_book_details(book_hash)
