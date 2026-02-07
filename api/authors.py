from fastapi import APIRouter, HTTPException
from app.model.author import Author
from app.crud.authors import create_author, get_author, delete_author, update_author, list_authors


router = APIRouter(prefix="/authors", tags=["Authors"])

@router.post("/")
async def add_author(author: Author):
    author_id = await create_author(author)
    return {"id": author_id, "status": "created"}

@router.get("/{id}")
async def read_author(id: str):
    author = await get_author(id)
    if not author:
        raise HTTPException(status_code=404, detail="Author Not Found")
    return author

@router.get("/")
async def get_author_list():
    author_list = await list_authors()
    return author_list

@router.delete("/{id}")
async def remove_author(id: str):
    result = await delete_author(id)
    return {"status": "deleted", "result": str(result)}

