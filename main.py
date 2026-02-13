from fastapi import FastAPI
from api.authors import router as author_router
from api.books import router as book_router
from api.readers import router as reader_router
from api.auth import router as auth_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

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
