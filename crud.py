from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
import models, schemas


# ── AUTHORS ───────────────────────────────────────────────────────────────────
def create_author(db: Session, author: schemas.AuthorCreate) -> models.Author:
    db_author = models.Author(**author.model_dump())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_author(db: Session, author_id: int) -> Optional[models.Author]:
    return db.query(models.Author).filter(models.Author.id == author_id).first()


def get_authors(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Author).offset(skip).limit(limit).all()


# ── BOOKS ─────────────────────────────────────────────────────────────────────
def create_book(db: Session, book: schemas.BookCreate) -> models.Book:
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    genre: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(models.Book)
    if genre:
        query = query.filter(models.Book.genre.ilike(f"%{genre}%"))
    if search:
        query = query.filter(
            or_(
                models.Book.title.ilike(f"%{search}%"),
                models.Book.description.ilike(f"%{search}%"),
            )
        )
    return query.offset(skip).limit(limit).all()


def update_book(
    db: Session, book_id: int, updates: schemas.BookUpdate
) -> Optional[models.Book]:
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True


# ── ORDERS ────────────────────────────────────────────────────────────────────
def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    # Validate stock and calculate total
    total = 0.0
    items_data = []
    for item in order.items:
        book = get_book(db, item.book_id)
        if not book:
            raise ValueError(f"Book id={item.book_id} not found")
        if book.stock < item.quantity:
            raise ValueError(
                f"Insufficient stock for '{book.title}' (available: {book.stock})"
            )
        total += book.price * item.quantity
        items_data.append((book, item.quantity))

    # Create order
    db_order = models.Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_address=order.customer_address,
        total_amount=round(total, 2),
    )
    db.add(db_order)
    db.flush()  # get db_order.id

    # Create items & deduct stock
    for book, qty in items_data:
        db_item = models.OrderItem(
            order_id=db_order.id,
            book_id=book.id,
            quantity=qty,
            unit_price=book.price,
        )
        db.add(db_item)
        book.stock -= qty

    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()


def update_order_status(
    db: Session, order_id: int, status: models.OrderStatus
) -> Optional[models.Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


# ── STATS ─────────────────────────────────────────────────────────────────────
def get_stats(db: Session) -> dict:
    total_books = db.query(func.count(models.Book.id)).scalar()
    total_authors = db.query(func.count(models.Author.id)).scalar()
    total_orders = db.query(func.count(models.Order.id)).scalar()
    total_revenue = db.query(func.sum(models.Order.total_amount)).scalar() or 0.0
    low_stock = (
        db.query(models.Book)
        .filter(models.Book.stock < 5)
        .with_entities(models.Book.id, models.Book.title, models.Book.stock)
        .all()
    )
    return {
        "total_books": total_books,
        "total_authors": total_authors,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "low_stock_books": [
            {"id": b.id, "title": b.title, "stock": b.stock} for b in low_stock
        ],
    }
