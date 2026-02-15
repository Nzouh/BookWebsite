from fastapi import APIRouter, HTTPException, status, Depends
from app.crud.books import (
    create_book, update_book, delete_book,
    get_book, get_book_full, get_chapter,
    list_books, list_books_alphabetical
)
from app.crud.authors import get_author_by_name, add_book_to_author, get_author_by_user_id
from app.model.book import Book
from api.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])

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
async def search_books(title: str):
    """Search books by title — returns card view results."""
    book_list = await list_books()
    searched_title = []
    
    for book in book_list:
        if title.lower() in book["title"].lower():
            searched_title.append(book)
    
    if not searched_title:
        return {"Result": "No books found"}
        
    return {"books": searched_title, "result": "found successfully"}

from app.services.annas_archive import find_books
from app.crud.download_jobs import create_job
from app.model.download_job import DownloadJob

@router.get("/external-search")
async def external_search_books(query: str):
    """
    Search books on Anna's Archive (external source).
    """
    if not query:
        return {"books": []}
        
    results = await find_books(query)
    return {"books": [b.to_dict() for b in results], "source": "Anna's Archive"}

@router.post("/request-download/{md5}")
async def request_book_download(md5: str, current_user: dict = Depends(get_current_user)):
    """
    Queue a book for download from Anna's Archive.
    """
    job = DownloadJob(book_hash=md5, user_id=current_user.get("sub"))
    job_id = await create_job(job)
    return {"job_id": job_id, "status": "queued"}

from fastapi import Query

@router.get("/batch")
async def get_books_batch(ids: list[str] = Query(default=[])):
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