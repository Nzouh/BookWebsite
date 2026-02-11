from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.user import UserInDB

database: AsyncIOMotorDatabase = get_db()

async def create_user(user_data: UserInDB):
    """Insert a new user document into the 'users' collection."""
    user = user_data.model_dump()
    collection = database["users"]
    result = await collection.insert_one(user)
    return str(result.inserted_id)

async def find_user_by_username(username: str):
    """Find a user document by username. Returns None if not found."""
    collection = database["users"]
    user = await collection.find_one({"username": username})
    if user:
        user["_id"] = str(user["_id"])
    return user
