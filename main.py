from fastapi import FastAPI
from api.authors import router as author_router
from api.books import router as book_router

app = FastAPI()

app.include_router(author_router)
app.include_router(book_router)

@app.get("/")
def home():
    return {"status" : "Backend is successfully up!"}
