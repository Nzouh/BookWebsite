from fastapi import APIRouter, HTTPException, status
from app.crud.books import create_book, update_book, delete_book, get_book, list_books
from app.model.book import Book

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", status_code=status.HTTP_201_CREATED)
# Only an author should be able to add a book to his own name, and so maybe 
# there should be a specific method available only to authors.
# This function serves as a way for a book to be created in general
async def add_book(book: Book):
    book_id = await create_book(book)
    return {"id": book_id, "status": "created"}

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