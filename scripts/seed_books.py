import asyncio
import requests
import sys
import os
sys.path.append(os.getcwd())
from motor.motor_asyncio import AsyncIOMotorClient
from app.model.book import Book, Chapter
from app.model.author import Author
import random

# Configuration
MONGO_URL = "mongodb://localhost:27017" # Using localhost for script run from host
DB_NAME = "book_db"
BOOKS_LIMIT = 15

# Dummy content for chapters
CHAPTER_TEMPLATES = [
    "It was a dark and stormy night. The wind howled through the trees like a wounded beast.",
    "The sun rose over the horizon, casting a long shadow across the valley.",
    "She knew that everything was about to change. The letter in her hand was the proof.",
    "They had been traveling for days, and the mountains were finally in sight.",
    "Deep in the heart of the city, there was a secret that few dared to speak of.",
    "The old clock on the wall ticked loudly, measuring the silence of the room.",
    "Sometimes the path you take is not the one you intended, but it is the one you need."
]

def generate_dummy_content(idx):
    content = ""
    for _ in range(5):
        content += random.choice(CHAPTER_TEMPLATES) + " "
    return content

async def seed_data():
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Clear existing data (optional, but good for a fresh start)
    # print("Clearing existing books and authors...")
    # await db.books.delete_many({})
    # await db.authors.delete_many({})

    print(f"Fetching {BOOKS_LIMIT} books from Open Library...")
    # Searching for general popular books
    url = f"https://openlibrary.org/search.json?q=popular&limit={BOOKS_LIMIT}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching from Open Library")
        return

    data = response.json()
    docs = data.get("docs", [])

    for doc in docs:
        title = doc.get("title")
        authors = doc.get("author_name", ["Unknown Author"])
        primary_author = authors[0]
        
        # Cover image URL
        cover_id = doc.get("cover_i")
        image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
        
        # Brief bio/summary
        subjects = doc.get("subject", [])
        biography = f"A fascinating book about {', '.join(subjects[:3])}." if subjects else "A must-read book found in the Open Library archives."

        # Create 3 chapters
        chapters = []
        for i in range(1, 4):
            chapters.append(Chapter(
                title=f"Chapter {i}: The Journey Begins" if i == 1 else f"Chapter {i}",
                content=generate_dummy_content(i),
                order=i
            ))

        # 1. Prepare Book Model
        book_obj = Book(
            title=title,
            author=primary_author,
            biography=biography,
            image=image_url,
            chapters=chapters
        )

        # 2. Insert Book
        book_data = book_obj.model_dump()
        result = await db.books.insert_one(book_data)
        book_id = str(result.inserted_id)
        print(f"Inserted Book: {title} (ID: {book_id})")

        # 3. Check/Create Author Profile
        author_profile = await db.authors.find_one({"name": primary_author})
        if not author_profile:
            new_author = Author(
                name=primary_author,
                biography=f"{primary_author} is a renowned author with a passion for storytelling.",
                book_list=[book_id]
            )
            await db.authors.insert_one(new_author.model_dump())
            print(f"  - Created new Author Profile for {primary_author}")
        else:
            await db.authors.update_one(
                {"_id": author_profile["_id"]},
                {"$push": {"book_list": book_id}}
            )
            print(f"  - Linked book to existing Author Profile: {primary_author}")

    print("\nSeeding complete! 🚀")

if __name__ == "__main__":
    asyncio.run(seed_data())
