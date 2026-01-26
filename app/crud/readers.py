from app.db.database import get_db
from app.model.reader import Reader
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIoMotorClient


database : AsyncIOMotorDatabase = get_db()

async def create_reader(reader_data: Reader):
    reader = reader_data.model_dump()

    collection = database["readers"]

    result = await collection.insert_one(reader)

    return result