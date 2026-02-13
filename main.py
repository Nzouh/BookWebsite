from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.authors import router as author_router
from api.books import router as book_router
from api.readers import router as reader_router
from api.auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
