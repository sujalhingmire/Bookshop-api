"""
Seed the database with sample authors, books, and an order.
Run once:  python seed.py
"""
from database import SessionLocal, engine, Base
import models, schemas, crud

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── AUTHORS ───────────────────────────────────────────────────────────────────
authors_data = [
    schemas.AuthorCreate(name="George Orwell", bio="English novelist and essayist.", nationality="British"),
    schemas.AuthorCreate(name="J.K. Rowling", bio="Author of the Harry Potter series.", nationality="British"),
    schemas.AuthorCreate(name="Gabriel García Márquez", bio="Colombian novelist and Nobel laureate.", nationality="Colombian"),
    schemas.AuthorCreate(name="Toni Morrison", bio="American novelist and Nobel laureate.", nationality="American"),
    schemas.AuthorCreate(name="Haruki Murakami", bio="Japanese writer known for surreal fiction.", nationality="Japanese"),
]

authors = [crud.create_author(db, a) for a in authors_data]
print(f"✅ Created {len(authors)} authors")

# ── BOOKS ─────────────────────────────────────────────────────────────────────
books_data = [
    schemas.BookCreate(title="1984", isbn="978-0451524935", genre="Dystopian Fiction",
        description="A chilling story of totalitarian surveillance.", price=9.99, stock=50,
        published_year=1949, author_id=authors[0].id),
    schemas.BookCreate(title="Animal Farm", isbn="978-0451526342", genre="Political Satire",
        description="A satirical allegory of the Russian Revolution.", price=7.99, stock=40,
        published_year=1945, author_id=authors[0].id),
    schemas.BookCreate(title="Harry Potter and the Sorcerer's Stone", isbn="978-0439708180",
        genre="Fantasy", description="The first book in the Harry Potter series.", price=12.99, stock=100,
        published_year=1997, author_id=authors[1].id),
    schemas.BookCreate(title="Harry Potter and the Chamber of Secrets", isbn="978-0439064873",
        genre="Fantasy", description="Harry's second year at Hogwarts.", price=12.99, stock=80,
        published_year=1998, author_id=authors[1].id),
    schemas.BookCreate(title="One Hundred Years of Solitude", isbn="978-0060883287",
        genre="Magical Realism", description="Epic saga of the Buendía family.", price=14.99, stock=30,
        published_year=1967, author_id=authors[2].id),
    schemas.BookCreate(title="Beloved", isbn="978-1400033416", genre="Historical Fiction",
        description="A powerful story about slavery's legacy.", price=13.99, stock=25,
        published_year=1987, author_id=authors[3].id),
    schemas.BookCreate(title="Norwegian Wood", isbn="978-0375704024", genre="Literary Fiction",
        description="A nostalgic story of loss and sexuality.", price=11.99, stock=35,
        published_year=1987, author_id=authors[4].id),
    schemas.BookCreate(title="Kafka on the Shore", isbn="978-1400079278", genre="Magical Realism",
        description="Two parallel stories intertwine in mysterious ways.", price=13.99, stock=3,
        published_year=2002, author_id=authors[4].id),
]

books = [crud.create_book(db, b) for b in books_data]
print(f"✅ Created {len(books)} books")

# ── SAMPLE ORDER ──────────────────────────────────────────────────────────────
order = crud.create_order(db, schemas.OrderCreate(
    customer_name="Alice Johnson",
    customer_email="alice@example.com",
    customer_address="42 Reading Lane, Booktown, BT1 2AB",
    items=[
        schemas.OrderItemCreate(book_id=books[0].id, quantity=1),
        schemas.OrderItemCreate(book_id=books[2].id, quantity=2),
    ]
))
print(f"✅ Created sample order #{order.id} — total: £{order.total_amount}")

db.close()
print("\n🎉 Database seeded successfully! Run: uvicorn main:app --reload")
