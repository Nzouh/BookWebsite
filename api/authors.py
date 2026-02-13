from fastapi import APIRouter, HTTPException, Depends
from app.model.author import Author
from app.crud.authors import (
    create_author, get_author, delete_author, update_author,
    list_authors, get_author_by_user_id, search_authors_by_name
)
from app.crud.books import get_books_by_ids
from api.auth import get_current_user

router = APIRouter(prefix="/authors", tags=["Authors"])

@router.get("/me")
async def get_my_author_profile(current_user: dict = Depends(get_current_user)):
    """Get the author profile for the currently logged-in user."""
    user_id = current_user["sub"]
    if "author" not in current_user.get("roles", []):
         raise HTTPException(status_code=403, detail="User is not an author")
         
    author = await get_author_by_user_id(user_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author Profile Not Found")
    return author

@router.post("/")
async def add_author(author: Author, current_user: dict = Depends(get_current_user)):
    author_id = await create_author(author)
    return {"id": author_id, "status": "created"}

@router.get("/")
async def get_author_list():
    author_list = await list_authors()
    return author_list

@router.get("/search")
async def search_authors(name: str):
    """Search for authors by name (partial, case-insensitive)."""
    results = await search_authors_by_name(name)
    if not results:
        return {"Result": "No authors found"}
    return {"authors": results, "result": "found successfully"}

@router.get("/{id}")
async def read_author(id: str):
    author = await get_author(id)
    if not author:
        raise HTTPException(status_code=404, detail="Author Not Found")
    return author

@router.get("/{id}/books")
async def get_author_books(id: str):
    """Get all books by a specific author, with full book details."""
    author = await get_author(id)
    if not author:
        raise HTTPException(status_code=404, detail="Author Not Found")
    
    if not author.get("book_list"):
        return {"books": [], "author": author["name"]}
    
    books = await get_books_by_ids(author["book_list"])
    return {"books": books, "author": author["name"]}

@router.put("/{id}")
async def modify_author(id: str, author: Author, current_user: dict = Depends(get_current_user)):
    """Update an author profile. Only the owner can edit their own profile."""
    existing = await get_author(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Author Not Found")
    
    # Ownership check: the author's user_id must match the logged-in user
    if existing.get("user_id") != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only edit your own author profile")
    
    try:
        await update_author(id, author)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
async def remove_author(id: str, current_user: dict = Depends(get_current_user)):
    existing = await get_author(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Author Not Found")
    
    # Ownership check
    if existing.get("user_id") != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only delete your own author profile")
    
    result = await delete_author(id)
    return {"status": "deleted", "result": str(result)}
