from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import SessionLocal, engine, Base
import models, schemas, crud

# ── Elasticsearch ─────────────────────────────────────────────────────────────
from elasticsearch_client import check_connection, create_indices
import search as es_search

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="📚 Bookshop API",
    description=(
        "A full-featured Bookshop REST API built with FastAPI & SQLAlchemy.\n\n"
        "**Search branch** — powered by Elasticsearch for full-text search, "
        "fuzzy matching, filters, highlights, and autocomplete."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── STARTUP: initialise ES indices ────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    if check_connection():
        print("✅ Elasticsearch connected")
        create_indices()
    else:
        print("⚠️  Elasticsearch not reachable — search endpoints will return 503")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_es():
    """Dependency: raise 503 if ES is not available."""
    if not check_connection():
        raise HTTPException(
            status_code=503,
            detail="Elasticsearch is unavailable. Please start ES and retry.",
        )


# ── ROOT ──────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, tags=["Home"])
def root():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


# ── BOOKS ─────────────────────────────────────────────────────────────────────
@app.post("/books/", response_model=schemas.BookOut, status_code=201, tags=["Books"])
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Add a new book to the shop."""
    db_book = crud.create_book(db, book)
    try:
        if check_connection():
            es_search.index_book(db_book)
    except Exception:
        pass
    return db_book


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
    try:
        if check_connection():
            es_search.index_book(updated)
    except Exception:
        pass
    return updated


@app.delete("/books/{book_id}", status_code=204, tags=["Books"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Remove a book from the shop."""
    if not crud.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    try:
        if check_connection():
            es_search.remove_book(book_id)
    except Exception:
        pass


# ── AUTHORS ───────────────────────────────────────────────────────────────────
@app.post("/authors/", response_model=schemas.AuthorOut, status_code=201, tags=["Authors"])
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """Register a new author."""
    db_author = crud.create_author(db, author)
    try:
        if check_connection():
            es_search.index_author(db_author)
    except Exception:
        pass
    return db_author


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


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH ENDPOINTS  (Elasticsearch-powered)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/search/books/", tags=["Search"])
def search_books(
    q: str = Query(..., min_length=1, description="Full-text search query"),
    genre: Optional[str] = Query(None, description="Filter by exact genre"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    published_year: Optional[int] = Query(None, description="Filter by published year"),
    in_stock: Optional[bool] = Query(None, description="Only return in-stock books"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _es=Depends(require_es),
):
    """
    **Elasticsearch-powered** full-text search for books.

    - Searches across `title` (3×), `author_name` (2×), and `description`
    - Supports fuzzy matching (typo-tolerant)
    - Returns highlighted snippets and relevance scores
    - Optional filters: `genre`, `min_price`, `max_price`, `published_year`, `in_stock`
    """
    return es_search.search_books(
        query=q,
        genre=genre,
        min_price=min_price,
        max_price=max_price,
        published_year=published_year,
        in_stock=in_stock,
        skip=skip,
        limit=limit,
    )


@app.get("/search/authors/", tags=["Search"])
def search_authors(
    q: str = Query(..., min_length=1, description="Full-text search query"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _es=Depends(require_es),
):
    """
    **Elasticsearch-powered** full-text search for authors.

    - Searches across `name` (3×) and `bio`
    - Supports fuzzy matching
    - Optional filter: `nationality`
    """
    return es_search.search_authors(
        query=q,
        nationality=nationality,
        skip=skip,
        limit=limit,
    )


@app.get("/search/suggestions/", tags=["Search"])
def search_suggestions(
    q: str = Query(..., min_length=1, description="Title prefix for autocomplete"),
    size: int = Query(5, ge=1, le=20),
    _es=Depends(require_es),
):
    """
    **Autocomplete** — returns book title suggestions matching a prefix.
    Ideal for powering a live search-as-you-type UI.
    """
    suggestions = es_search.get_search_suggestions(prefix=q, size=size)
    return {"query": q, "suggestions": suggestions}


@app.post("/search/reindex/", tags=["Search"], status_code=200)
def reindex_all(db: Session = Depends(get_db), _es=Depends(require_es)):
    """
    **Re-index** all books and authors from the database into Elasticsearch.
    Use this after importing bulk data or if the index gets out of sync.
    """
    books = db.query(models.Book).all()
    authors = db.query(models.Author).all()

    books_count = es_search.bulk_index_books(books)
    authors_count = es_search.bulk_index_authors(authors)

    return {
        "status": "ok",
        "books_indexed": books_count,
        "authors_indexed": authors_count,
    }


@app.get("/search/health/", tags=["Search"])
def search_health():
    """Check Elasticsearch connection status."""
    connected = check_connection()
    return {
        "elasticsearch": "connected" if connected else "unavailable",
        "status": "ok" if connected else "degraded",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
