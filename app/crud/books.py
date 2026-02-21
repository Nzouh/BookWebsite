from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.book import Book
from bson import ObjectId

database: AsyncIOMotorDatabase = get_db()

# Projection that excludes chapters — used for listing/searching (Netflix card view)
# Only returns: _id, title, author, image
CARD_PROJECTION = {"chapters": 0, "biography": 0}

# Projection that excludes chapter CONTENT but keeps chapter titles/order (book detail view)
# Returns everything except the heavy content field inside each chapter
# MongoDB can't partially project nested arrays with simple projections,
# so we'll handle this in the get_book function by stripping content in Python
DETAIL_PROJECTION = None  # we fetch full doc and strip in code


async def create_book(book_data: Book):
    book = book_data.model_dump()
    collection = database["books"]
    result = await collection.insert_one(book)
    return str(result.inserted_id)

async def update_book(_id: str, book_data: Book):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")

    book = book_data.model_dump()
    collection = database["books"]
    result = await collection.update_one({"_id": oid}, {"$set": book})
    return result

async def delete_book(_id: str):
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")
        
    collection = database["books"]
    result = await collection.delete_one({"_id": oid})
    return result

async def get_book(_id: str):
    """Get a single book with chapter list (titles + order only, no chapter content).
    Used for the book detail page."""
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")

    collection = database["books"]
    book = await collection.find_one({"_id": oid})
    if book:
        book["_id"] = str(book["_id"])
        # Strip chapter content — only keep title and order for the table of contents
        if "chapters" in book:
            book["chapters"] = [
                {"title": ch["title"], "order": ch["order"]}
                for ch in book["chapters"]
            ]
    return book

async def get_book_full(_id: str):
    """Get the full book document including all chapter content.
    Used internally (e.g. for update checks)."""
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")

    collection = database["books"]
    book = await collection.find_one({"_id": oid})
    if book:
        book["_id"] = str(book["_id"])
    return book

async def get_chapter(_id: str, chapter_order: int):
    """Get a specific chapter from a book by its order number."""
    try:
        oid = ObjectId(_id)
    except Exception:
        raise ValueError("Must be a valid id format")

    collection = database["books"]
    book = await collection.find_one({"_id": oid})
    if not book:
        return None
    
    for ch in book.get("chapters", []):
        if ch["order"] == chapter_order:
            return ch
    return None

async def list_books():
    """List all books — card view only (title, author, image). No chapters or biography."""
    collection = database["books"]
    books = []
    async for book in collection.find({}, CARD_PROJECTION):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books

async def list_books_alphabetical():
    """Return all books sorted alphabetically — card view only."""
    collection = database["books"]
    books = []
    async for book in collection.find({}, CARD_PROJECTION).sort("title", 1):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books

async def get_books_by_ids(book_ids: list[str]):
    """Given a list of book ID strings, return card-view book documents."""
    collection = database["books"]
    oids = []
    for bid in book_ids:
        try:
            oids.append(ObjectId(bid))
        except Exception:
            continue
    books = []
    async for book in collection.find({"_id": {"$in": oids}}, CARD_PROJECTION):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books

async def get_book_by_hash(book_hash: str):
    collection = database["books"]
    book = await collection.find_one({"md5": book_hash})
    if book:
        book["_id"] = str(book["_id"])
    return book

async def update_book_status(book_hash: str, status: str, error: str = ""):
    collection = database["books"]
    await collection.update_one(
        {"md5": book_hash},
        {"$set": {"status": status, "error_message": error}}
    )

async def delete_failed_books(cutoff_time: float):
    collection = database["books"]
    result = await collection.delete_many({
        "status": "error",
        "updated_at": {"$lt": cutoff_time}
    })
    return result.deleted_count


async def search_books_local(query: str):
    """Search books in the local catalogue by title (case-insensitive partial match)."""
    collection = database["books"]
    books = []
    async for book in collection.find(
        {"title": {"$regex": query, "$options": "i"}},
        CARD_PROJECTION
    ):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books


async def import_book_from_external(anna_book) -> str:
    """
    Import a book from Anna's Archive scraper data into the local catalogue.
    
    Args:
        anna_book: A Book dataclass from annas_archive.py (scraped data)
    
    Returns:
        The string ID of the newly created book document.
    """
    from datetime import datetime

    new_book = Book(
        title=anna_book.title or "Unknown Title",
        author=anna_book.authors or "Unknown Author",
        description=anna_book.description or "",
        biography=anna_book.description or "",
        image=anna_book.cover_url or None,
        cover_url=anna_book.cover_url or None,
        md5=anna_book.hash,
        download_url=anna_book.url or None,
        format=anna_book.format or None,
        size=anna_book.size or None,
        language=anna_book.language or None,
        publisher=anna_book.publisher or None,
        year=anna_book.year or None,
        isbn=anna_book.isbn or None,
        source="external",
        status="imported",
        created_at=datetime.now().timestamp(),
        updated_at=datetime.now().timestamp(),
    )
    return await create_book(new_book)


async def update_book_chapters(book_id: str, chapters: list[dict]):
    """Update the chapters field of a book after parsing."""
    from datetime import datetime
    try:
        oid = ObjectId(book_id)
    except Exception:
        raise ValueError("Must be a valid id format")
    collection = database["books"]
    await collection.update_one(
        {"_id": oid},
        {"$set": {"chapters": chapters, "status": "ready", "updated_at": datetime.now().timestamp()}}
    )