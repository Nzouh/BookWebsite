from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.author import Author



database: AsyncIOMotorDatabase = get_db()
#CRUD methods : Create, Read, Update, Delete

#Implement the Create method

async def create_author(author_data: Author):
    author = author_data.model_dump()
    collection = database["authors"]

    result = await collection.insert_one(author)

    return result
    