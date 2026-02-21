from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.crud.books import (
    create_book, update_book, delete_book,
    get_book, get_book_full, get_chapter,
    list_books, list_books_alphabetical,
    get_books_by_ids, search_books_local,
    import_book_from_external, get_book_by_hash,
    update_book_chapters
)
from app.crud.authors import get_author_by_name, add_book_to_author, get_author_by_user_id
from app.model.book import Book
from api.auth import get_current_user
from app.services.annas_archive import AnnasArchiveService, find_books, get_book_metadata
from app.crud.download_jobs import create_job
from app.model.download_job import DownloadJob

router = APIRouter(prefix="/books", tags=["Books"])

# Shared service instance
_anna_service = AnnasArchiveService()


# ─── Discovery & Search ──────────────────────────────────────────────

@router.get("/")
async def all_books():
    """List all books — card view (title, author, image only)."""
    result = await list_books()
    return result

@router.get("/featured")
async def featured_books():
    """Featured books sorted A-Z — card view."""
    result = await list_books_alphabetical()
    return result

@router.get("/search")
async def search_books(q: str = "", title: str = ""):
    """
    Unified search: returns results from Anna's Archive (external)
    and from the local catalogue.

    Accepts either `q` (new) or `title` (legacy) as the query parameter.
    """
    query = q or title
    if not query.strip():
        return {"local": [], "external": []}

    # Run both searches
    local_results = await search_books_local(query)
    
    try:
        external_results = await _anna_service.search(query, limit=20)
        external_dicts = [b.to_dict() for b in external_results]
    except Exception:
        external_dicts = []

    return {
        "local": local_results,
        "external": external_dicts,
    }

@router.get("/external-search")
async def external_search_books(query: str = ""):
    """
    Search books on Anna's Archive (external source).
    Kept for backward compatibility — same data as /search but external-only.
    """
    if not query:
        return {"books": []}
        
    try:
        results = await _anna_service.search(query)
        return {"books": [b.to_dict() for b in results], "source": "Anna's Archive"}
    except Exception:
        return {"books": [], "source": "Anna's Archive"}


# ─── External Book Details & Import ──────────────────────────────────

@router.get("/external/{md5}")
async def get_external_book_details(md5: str):
    """
    Fetch detailed metadata for an external book from Anna's Archive.
    Does NOT save anything to the database — this is a preview.
    """
    # Check if we already have this book locally
    existing = await get_book_by_hash(md5)
    if existing:
        return {
            "book": existing,
            "source": "local",
            "local_id": existing["_id"],
        }

    details = await _anna_service.get_book_details(md5)
    if not details:
        raise HTTPException(status_code=404, detail="Book not found on Anna's Archive")

    return {
        "book": details.to_dict(),
        "source": "external",
        "local_id": None,
    }


@router.post("/import/{md5}")
async def import_external_book(md5: str, current_user: dict = Depends(get_current_user)):
    """
    Import an external book into the local catalogue.
    Scrapes full metadata from Anna's Archive and creates a Book record.
    """
    # Check if already imported
    existing = await get_book_by_hash(md5)
    if existing:
        return {"id": existing["_id"], "status": "already_imported"}

    # Fetch full details from Anna's Archive
    details = await _anna_service.get_book_details(md5)
    if not details:
        raise HTTPException(status_code=404, detail="Book not found on Anna's Archive")

    # Import into local catalogue
    book_id = await import_book_from_external(details)

    return {"id": book_id, "status": "imported"}


# ─── Download & Read ─────────────────────────────────────────────────

@router.post("/{book_id}/download")
async def download_book(book_id: str, current_user: dict = Depends(get_current_user)):
    """
    Kick off the download + chapter parsing pipeline for an imported book.
    Creates a DownloadJob that the DownloadService processes in background.
    """
    book = await get_book_full(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")

    if not book.get("md5"):
        raise HTTPException(status_code=400, detail="Book has no external hash — cannot download")

    if book.get("status") == "ready" and book.get("chapters"):
        return {"status": "already_ready", "message": "Book is already downloaded and parsed"}

    # Create a download job
    job = DownloadJob(book_hash=book["md5"], user_id=current_user.get("sub"))
    job_id = await create_job(job)

    return {"job_id": job_id, "status": "queued"}


# ─── Batch & Individual Book Access ──────────────────────────────────

@router.get("/batch")
async def get_books_batch_endpoint(ids: list[str] = Query(default=[])):
    """Get multiple books by detailed ID list. Returns card view."""
    if not ids:
        return []
    return await get_books_by_ids(ids)


@router.get("/{book_id}")
async def read_book(book_id: str):
    """Get book detail — biography + chapter list (titles only, no content)."""
    book = await get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    return book

@router.get("/{book_id}/chapters/{chapter_order}")
async def read_chapter(book_id: str, chapter_order: int):
    """Read a specific chapter's content."""
    chapter = await get_chapter(book_id, chapter_order)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter Not Found")
    return chapter


# ─── Book CRUD (Author Operations) ───────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_book(book: Book, current_user: dict = Depends(get_current_user)):
    # Only authors can create books
    if "author" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Only authors can create books")
    
    # 1. Create the book
    book_id = await create_book(book)
    
    # 2. Try to find the author by name
    author = await get_author_by_name(book.author)
    
    status_msg = "created"
    if author:
        # 3. Link the book to the author's list
        await add_book_to_author(author["_id"], book_id)
        status_msg = "created and linked to author"
    else:
        status_msg = "created (author not found in database)"

    return {"id": book_id, "status": status_msg}

@router.put("/{book_id}")
async def modify_book(book_id: str, book: Book, current_user: dict = Depends(get_current_user)):
    # Only authors can edit books
    if "author" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Only authors can edit books")
    
    # Check ownership
    existing_book = await get_book_full(book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    
    author_profile = await get_author_by_user_id(current_user["sub"])
    if not author_profile or author_profile["name"] != existing_book["author"]:
        raise HTTPException(status_code=403, detail="You can only edit your own books")
    
    try:
        await update_book(book_id, book)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{book_id}")
async def remove_book(book_id: str, current_user: dict = Depends(get_current_user)):
    # Check ownership
    existing_book = await get_book_full(book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    
    author_profile = await get_author_by_user_id(current_user["sub"])
    if not author_profile or author_profile["name"] != existing_book["author"]:
        raise HTTPException(status_code=403, detail="You can only delete your own books")
    
    result = await delete_book(book_id)
    return {"status": "deleted", "result": str(result.deleted_count)}


# ─── Legacy Endpoints ────────────────────────────────────────────────

@router.post("/request-download/{md5}")
async def request_book_download(md5: str, current_user: dict = Depends(get_current_user)):
    """
    Queue a book for download from Anna's Archive. (Legacy endpoint)
    """
    job = DownloadJob(book_hash=md5, user_id=current_user.get("sub"))
    job_id = await create_job(job)
    return {"job_id": job_id, "status": "queued"}