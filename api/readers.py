from fastapi import APIRouter, HTTPException, status, Depends
from app.model.readers import Reader 
from app.crud.readers import (
    get_reader, 
    list_readers, 
    create_reader, 
    delete_reader, 
    update_reader,
    add_book_to_reader_list,
    get_reader_by_user_id
)
from api.auth import get_current_user

router = APIRouter(prefix="/readers", tags=["Readers"])

@router.get("/me")
async def get_my_reader_profile(current_user: dict = Depends(get_current_user)):
    """Get the reader profile for the currently logged-in user."""
    user_id = current_user["sub"]
    reader = await get_reader_by_user_id(user_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader Profile Not Found")
    return reader

@router.post("/", status_code=status.HTTP_201_CREATED)
async def make_reader(reader: Reader, current_user: dict = Depends(get_current_user)):
    reader_id = await create_reader(reader)
    return {"id": reader_id, "status": "created"}

@router.get("/")
async def get_all_readers():
    return await list_readers()

@router.get("/{id}")
async def read_reader(id: str):
    reader = await get_reader(id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader Not Found")
    return reader

@router.put("/{id}")
async def modify_reader(id: str, reader: Reader, current_user: dict = Depends(get_current_user)):
    try:
        await update_reader(id, reader)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{id}")
async def remove_reader(id: str, current_user: dict = Depends(get_current_user)):
    result = await delete_reader(id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reader Not Found")
    return {"status": "deleted"}

@router.post("/{reader_id}/add-book")
async def add_book_to_list(reader_id: str, book_id: str, list_name: str, current_user: dict = Depends(get_current_user)):
    """
    Adds a book to a specific list: 'favorites', 'in_progress', or 'finished'
    """
    try:
        await add_book_to_reader_list(reader_id, book_id, list_name)
        return {"status": f"Book added to {list_name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
