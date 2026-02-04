from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.author import Author
from bson import ObjectId



database: AsyncIOMotorDatabase = get_db()
#CRUD methods : Create, Read, Update, Delete

#Implement the Create method

async def create_author(author_data: Author):
    author = author_data.model_dump()
    collection = database["authors"]

    result = await collection.insert_one(author)

    return  str(result.inserted_id)
   
    
async def get_author(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    
    collection = database["authors"]
    author = await collection.find_one({"_id": oid})
    
    if author:
        author["_id"] = str(author["_id"])
        return author
    return None

async def list_authors():
    collection = database["authors"]
    authors = []
    async for author in collection.find():
        author["_id"] = str(author["_id"])
        authors.append(author)
    return authors

    

async def delete_author(_id : str):

    try:
        oid = ObjectId(_id)
    except: 
        raise ValueError("must be a valid id format")
    
    collection = database["authors"]
    
    result = await collection.delete_one({"_id": oid})

    return result


async def update_author(_id: str, author_data: Author):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    
    collection = database["authors"]

    # Use exclude_unset=True so that only fields explicitly provided in the request are updated
    # This allows for partial updates if the Pydantic model supports it (all fields Optional)
    # Since Author fields (name, book_list) are required currently, this defaults to a full update.
    update_data = author_data.model_dump(exclude_unset=True)

    result = await collection.update_one({"_id": oid}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise ValueError("Author not found")

    return result
