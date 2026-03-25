# 📚 The Grand Bookshop — FastAPI Application

A full-featured Bookshop REST API + Web UI built with **FastAPI**, **SQLAlchemy**, and **Python**.

## ✨ Features

- **Books** — CRUD: create, list, search, filter by genre, update, delete
- **Authors** — Register authors and link them to books
- **Orders** — Place orders with stock validation, order status workflow
- **Stats** — Live dashboard: total books, authors, orders, revenue, low-stock alerts
- **Beautiful Web UI** — Served directly from FastAPI at `/`
- **Interactive API Docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **SQLite** by default — swap to PostgreSQL/MySQL in `database.py`

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the database with sample data
```bash
python seed.py
```

### 3. Start the server
```bash
uvicorn main:app --reload
```

### 4. Open the app
| URL | Description |
|-----|-------------|
| http://localhost:8000 | 📚 Bookshop Web UI |
| http://localhost:8000/docs | 🔧 Swagger API Docs |
| http://localhost:8000/redoc | 📄 ReDoc API Docs |

---

## 📁 Project Structure

```
bookshop/
├── main.py          # FastAPI app, routes
├── database.py      # SQLAlchemy engine & session
├── models.py        # DB models: Author, Book, Order, OrderItem
├── schemas.py       # Pydantic schemas (validation & serialization)
├── crud.py          # Database operations
├── seed.py          # Sample data loader
├── requirements.txt
└── templates/
    └── index.html   # Frontend UI
```

---

## 🔌 API Endpoints

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/books/` | Add a new book |
| `GET` | `/books/` | List books (with `?search=` & `?genre=` filters) |
| `GET` | `/books/{id}` | Get book by ID |
| `PUT` | `/books/{id}` | Update a book |
| `DELETE` | `/books/{id}` | Delete a book |

### Authors
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/authors/` | Add an author |
| `GET` | `/authors/` | List authors |
| `GET` | `/authors/{id}` | Get author by ID |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders/` | Place an order |
| `GET` | `/orders/` | List all orders |
| `GET` | `/orders/{id}` | Get order by ID |
| `PATCH` | `/orders/{id}/status` | Update order status |

### Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stats/` | Shop statistics |

---

## 🗄️ Switching to PostgreSQL

In `database.py`, replace the URL:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/bookshop"
```
Remove `connect_args` (SQLite-only), then install `psycopg2`:
```bash
pip install psycopg2-binary
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Server | Uvicorn |
| Frontend | Vanilla JS + HTML/CSS |
