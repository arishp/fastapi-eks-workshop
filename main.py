from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Workshop API", version="1.0.0")

# In-memory database to avoid RDS/PostgreSQL debugging during the lab
FAKE_DB = {
    1: {"id": 1, "title": "The C Programming Language", "author": "Kernighan & Ritchie"},
    2: {"id": 2, "title": "Introduction to Algorithms", "author": "Cormen"},
}

class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str

# CRITICAL FOR AWS: The Target Group health check will hit the root path ('/') by default. 
# If this returns 404, the Load Balancer will mark the EKS pods as unhealthy and drop traffic.
@app.get("/")
def health_check():
    return {"status": "healthy", "message": "API is running successfully in EKS!"}

@app.get("/books", response_model=List[Book])
def get_all_books():
    return list(FAKE_DB.values())

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    if book_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail="Book not found")
    return FAKE_DB[book_id]

@app.post("/books", response_model=Book, status_code=201)
def create_book(book: Book):
    new_id = max(FAKE_DB.keys()) + 1 if FAKE_DB else 1
    book_dict = book.model_dump()
    book_dict["id"] = new_id
    FAKE_DB[new_id] = book_dict
    return book_dict


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail="Book not found")
    del FAKE_DB[book_id]
    return {"message": "Book deleted successfully"}