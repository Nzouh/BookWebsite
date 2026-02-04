#plan: we need to implement CRUD : Create, Read, Update, Delete basic functions

#We import motor database, we import the appropriate model (book.py) and we 
#import the database. Next, we need to create a

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.db.database import get_db
from app.model.book import Book
from bson import ObjectId

database : AsyncIOMotorDatabase = get_db()

async def create_book(book_data: Book):
    book = book_data.model_dump()
    
    collection = database["books"]

    result = await collection.insert_one(book)

    return result


async def update_book(_id: str ,book_data:Book):

    try:
        oid = ObjectId(_id)

    
    except ValueError:
        raise ValueError("Must be a valid id format")


    book = book_data.model_dump()

    collection = database["books"]

    result = await collection.update_one({"_id" : oid}, {"$set" : book})

    return result

async def delete_book(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["books"]
    result = await collection.delete_one({"_id" : oid})
    return result


async def get_book(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["books"]
    book = await collection.find_one({"_id" : oid})
    if book:
        book["_id"] = str(book["_id"])
    return book

async def list_books():
    collection = database["books"]
    books = []
    async for book in collection.find():
        book["_id"] = str(book["_id"])
        books.append(book)
    return books
    