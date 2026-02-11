from fastapi import APIRouter, HTTPException, status, Depends
from app.crud.books import create_book, update_book, delete_book, get_book, list_books, list_books_alphabetical
from app.crud.authors import get_author_by_name, add_book_to_author, get_author_by_user_id
from app.model.book import Book
from api.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/")
async def all_books():
    result = await list_books()
    return result

@router.get("/featured")
async def featured_books():
    """Returns books sorted alphabetically by title."""
    result = await list_books_alphabetical()
    return result

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

@router.get("/search")
async def search_books(title: str):
    book_list = await list_books()
    searched_title = []
    
    for book in book_list:
        if title.lower() in book["title"].lower():
            searched_title.append(book)
    
    if not searched_title:
        return {"Result": "No books found"}
        
    return {"books": searched_title, "result": "found successfully"}

@router.get("/{book_id}")
async def read_book(book_id: str):
    book = await get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    return book

@router.put("/{book_id}")
async def modify_book(book_id: str, book: Book, current_user: dict = Depends(get_current_user)):
    # Only authors can edit books
    if "author" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Only authors can edit books")
    
    # Check ownership: the logged-in user must own the author profile that matches the book's author
    existing_book = await get_book(book_id)
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
    existing_book = await get_book(book_id)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    
    author_profile = await get_author_by_user_id(current_user["sub"])
    if not author_profile or author_profile["name"] != existing_book["author"]:
        raise HTTPException(status_code=403, detail="You can only delete your own books")
    
    result = await delete_book(book_id)
    return {"status": "deleted", "result": str(result.deleted_count)}