from fastapi import FastAPI
from api.authors import router as author_router

app = FastAPI()

app.include_router(author_router)

@app.get("/")
def home():
    return {"status" : "Backend is successfully up!"}

