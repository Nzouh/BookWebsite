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
   
    
async def read_books(_id : str):
    try:
        oid = ObjectId(_id)
    except:
        raise ValueError("Must be a valid id format")
    
    collection = database["authors"]

    print("all books from the author:")
    author = await collection.find_one({"_id" : oid})

    if author:
        for book in author.get("book_list", []):
            print(book)
    else:
        print("author not found")

    

async def delete_author(_id : str):

    try:
        oid = ObjectId(_id)
    except: 
        raise ValueError("must be a valid id format")
    
    collection = database["authors"]
    
    result = await collection.delete_one({"_id": oid})

    return result

