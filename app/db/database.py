from motor.motor_asyncio import AsyncIOMotorClient

#The Address
MONGO_URL = "mongodb://db:27017"

#The Client
client = AsyncIOMotorClient(MONGO_URL)

#Creating the book database
#If book_db doesn't exist yet, it creates it automatically bc MongoDB operates intelligently
database = client.book_db


#Repositories will run this function 
def get_db():
    return database