from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.readers import Reader
from bson import ObjectId

database : AsyncIOMotorDatabase = get_db()

async def create_reader(reader_data: Reader):
    reader = reader_data.model_dump()
    collection = database["readers"]
    result = await collection.insert_one(reader)
    return str(result.inserted_id)

async def get_reader(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["readers"]
    reader = await collection.find_one({"_id": oid})
    if reader:
        reader["_id"] = str(reader["_id"])
    return reader

async def update_reader(_id: str, reader_data: Reader):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["readers"]
    update_data = reader_data.model_dump(exclude_unset=True)
    result = await collection.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise ValueError("Reader not found")
    return result

async def delete_reader(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["readers"]
    result = await collection.delete_one({"_id": oid})
    return result

async def list_readers():
    collection = database["readers"]
    readers = []
    async for reader in collection.find():
        reader["_id"] = str(reader["_id"])
        readers.append(reader)
    return readers

async def add_book_to_reader_list(reader_id: str, book_id: str, list_name: str):
    """
    Helper to add a book ID to one of the reader's lists (favorites, in_progress, finished)
    """
    if list_name not in ["favorites", "in_progress", "finished"]:
        raise ValueError("Invalid list name")
        
    try:
        oid = ObjectId(reader_id)
    except Exception:
        raise ValueError("Must be a valid id format")
        
    collection = database["readers"]
    # $addToSet ensures no duplicates
    # $pull from other lists if needed? For now just add.
    result = await collection.update_one(
        {"_id": oid},
        {"$addToSet": {list_name: book_id}}
    )
    return result