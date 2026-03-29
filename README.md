# 📚 The Grand Bookshop — FastAPI Application

A full-featured Bookshop REST API + Web UI built with **FastAPI**, **SQLAlchemy**, and **Python**.

## ✨ Features

- **Books** — CRUD: create, list, search, filter by genre, update, delete
- **Authors** — Register authors and link them to books
- **Orders** — Place orders with stock validation, order status workflow
- **Stats** — Live dashboard: total books, authors, orders, revenue, low-stock alerts
- **🔍 Elasticsearch Search** — Full-text, fuzzy, filtered search + autocomplete (search branch)
- **Beautiful Web UI** — Served directly from FastAPI at `/`
- **Interactive API Docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **SQLite** by default — swap to PostgreSQL/MySQL in `database.py`

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Elasticsearch (required for search endpoints)
```bash
# Docker (recommended)
docker run -d --name es -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.0
```

### 3. Seed the database with sample data
```bash
python seed.py
```

### 4. Start the server
```bash
uvicorn main:app --reload
```

### 5. Index existing data into Elasticsearch
```bash
curl -X POST http://localhost:8000/search/reindex/
```

### 6. Open the app
| URL | Description |
|-----|-------------|
| http://localhost:8000 | 📚 Bookshop Web UI |
| http://localhost:8000/docs | 🔧 Swagger API Docs |
| http://localhost:8000/redoc | 📄 ReDoc API Docs |
| http://localhost:8000/search/health/ | 🔍 ES connection health |

---

## 📁 Project Structure

```
bookshop/
├── main.py                  # FastAPI app, routes (incl. search endpoints)
├── database.py              # SQLAlchemy engine & session
├── models.py                # DB models: Author, Book, Order, OrderItem
├── schemas.py               # Pydantic schemas (validation & serialization)
├── crud.py                  # Database operations
├── elasticsearch_client.py  # ES connection & index setup  ← NEW
├── search.py                # ES indexing & search helpers ← NEW
├── seed.py                  # Sample data loader
├── requirements.txt
└── templates/
    └── index.html           # Frontend UI
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

### 🔍 Search (Elasticsearch)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/search/books/` | Full-text book search with filters |
| `GET` | `/search/authors/` | Full-text author search |
| `GET` | `/search/suggestions/` | Autocomplete title suggestions |
| `POST` | `/search/reindex/` | Re-index all DB records into ES |
| `GET` | `/search/health/` | Elasticsearch health check |

#### Book Search Query Parameters
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | **Required.** Full-text query |
| `genre` | string | Filter by genre (exact match) |
| `min_price` | float | Minimum price |
| `max_price` | float | Maximum price |
| `published_year` | int | Filter by publication year |
| `in_stock` | bool | Only return in-stock books |
| `skip` / `limit` | int | Pagination |

#### Example Searches
```bash
# Fuzzy full-text search
GET /search/books/?q=orwel

# Filter by genre + price
GET /search/books/?q=magic&genre=Fantasy&max_price=13

# In-stock books only
GET /search/books/?q=harry&in_stock=true

# Author search
GET /search/authors/?q=murakami

# Autocomplete
GET /search/suggestions/?q=har
```

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
| Search Engine | Elasticsearch 8.x |
| Server | Uvicorn |
| Frontend | Vanilla JS + HTML/CSS |
