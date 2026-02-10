from fastapi import APIRouter, HTTPException, status
from app.crud.books import create_book, update_book, delete_book, get_book, list_books
from app.crud.authors import get_author_by_name, add_book_to_author
from app.model.book import Book

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/")
async def all_books():
    result = await list_books()
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_book(book: Book):
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
    # list_books is async, so we must await it
    book_list = await list_books()
    searched_title = []
    
    for book in book_list:
        # book is a dictionary, so we access it with ["title"]
        # using 'in' for partial match, usage of == is also fine but strict
        if title.lower() in book["title"].lower():
            searched_title.append(book)
    
    if not searched_title:
        return {"Result": "No books found"}
        
    return {"books": searched_title, "result": "found successfully"}

@router.get("/{book_id}")
async def read_book(book_id: str):
    # Fixed syntax error: removed ': str' from function call
    book = await get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found")
    return book

@router.delete("/{book_id}")
async def remove_book(book_id: str):
    result = await delete_book(book_id)
    return {"status": "deleted", "result": str(result.deleted_count)}