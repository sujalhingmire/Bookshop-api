from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import SessionLocal, engine, Base
import models, schemas, crud

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="📚 Bookshop API",
    description="A full-featured Bookshop REST API built with FastAPI & SQLAlchemy",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ROOT ──────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, tags=["Home"])
def root():
    with open("templates/index.html", encoding="utf-8") as f:
       return f.read()



# ── BOOKS ─────────────────────────────────────────────────────────────────────
@app.post("/books/", response_model=schemas.BookOut, status_code=201, tags=["Books"])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Add a new book to the shop."""
    return crud.create_book(db, book)


@app.get("/books/", response_model=List[schemas.BookOut], tags=["Books"])
def list_books(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    genre: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all books with optional genre filter / keyword search."""
    return crud.get_books(db, skip=skip, limit=limit, genre=genre, search=search)


@app.get("/books/{book_id}", response_model=schemas.BookOut, tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve a single book by ID."""
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=schemas.BookOut, tags=["Books"])
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    """Update an existing book."""
    updated = crud.update_book(db, book_id, book)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


@app.delete("/books/{book_id}", status_code=204, tags=["Books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the shop."""
    if not crud.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Book not found")


# ── AUTHORS ───────────────────────────────────────────────────────────────────
@app.post("/authors/", response_model=schemas.AuthorOut, status_code=201, tags=["Authors"])
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """Register a new author."""
    return crud.create_author(db, author)


@app.get("/authors/", response_model=List[schemas.AuthorOut], tags=["Authors"])
def list_authors(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all authors."""
    return crud.get_authors(db, skip=skip, limit=limit)


@app.get("/authors/{author_id}", response_model=schemas.AuthorOut, tags=["Authors"])
def get_author(author_id: int, db: Session = Depends(get_db)):
    """Get a single author and their books."""
    author = crud.get_author(db, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


# ── ORDERS ────────────────────────────────────────────────────────────────────
@app.post("/orders/", response_model=schemas.OrderOut, status_code=201, tags=["Orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Place a new order."""
    try:
        return crud.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/", response_model=List[schemas.OrderOut], tags=["Orders"])
def list_orders(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all orders."""
    return crud.get_orders(db, skip=skip, limit=limit)


@app.get("/orders/{order_id}", response_model=schemas.OrderOut, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order by ID."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=schemas.OrderOut, tags=["Orders"])
def update_order_status(
    order_id: int,
    payload: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update order status (pending → confirmed → shipped → delivered)."""
    order = crud.update_order_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# ── STATS ─────────────────────────────────────────────────────────────────────
@app.get("/stats/", tags=["Stats"])
def get_stats(db: Session = Depends(get_db)):
    """Bookshop summary statistics."""
    return crud.get_stats(db)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
