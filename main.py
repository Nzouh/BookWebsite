import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables from .env file if it exists
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from api.authors import router as author_router
from api.books import router as book_router
from api.readers import router as reader_router
from api.auth import router as auth_router

app = FastAPI()

# Load origins from .env or default to local development ports
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3004,http://localhost:3005")
origins = [origin.strip() for origin in cors_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(author_router)
app.include_router(book_router)
app.include_router(reader_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {"status" : "Backend is successfully up!"}
