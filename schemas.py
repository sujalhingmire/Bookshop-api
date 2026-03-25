from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from models import OrderStatus


# ── AUTHOR ────────────────────────────────────────────────────────────────────
class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    bio: Optional[str] = None
    nationality: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── BOOK ──────────────────────────────────────────────────────────────────────
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=250)
    isbn: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    cover_url: Optional[str] = None
    published_year: Optional[int] = None
    author_id: Optional[int] = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    cover_url: Optional[str] = None
    published_year: Optional[int] = None
    author_id: Optional[int] = None


class BookOut(BookBase):
    id: int
    created_at: datetime
    author: Optional[AuthorOut] = None

    class Config:
        from_attributes = True


# ── ORDER ─────────────────────────────────────────────────────────────────────
class OrderItemCreate(BaseModel):
    book_id: int
    quantity: int = Field(..., ge=1)


class OrderItemOut(BaseModel):
    id: int
    book_id: int
    quantity: int
    unit_price: float
    book: Optional[BookOut] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=150)
    customer_email: str
    customer_address: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    customer_address: Optional[str]
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True
