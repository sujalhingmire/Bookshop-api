"""
Elasticsearch indexing & search helpers.
Provides functions to index, remove, and search books/authors.
"""
from typing import Optional, List, Dict, Any
from elasticsearch import NotFoundError

from elasticsearch_client import es, BOOKS_INDEX, AUTHORS_INDEX
import models


# ── BOOK INDEXING ─────────────────────────────────────────────────────────────

def book_to_doc(book: models.Book) -> Dict[str, Any]:
    """Convert a Book ORM object to an ES document dict."""
    return {
        "id":                  book.id,
        "title":               book.title,
        "isbn":                book.isbn,
        "genre":               book.genre,
        "description":         book.description,
        "price":               book.price,
        "stock":               book.stock,
        "cover_url":           book.cover_url,
        "published_year":      book.published_year,
        "author_id":           book.author_id,
        "author_name":         book.author.name if book.author else None,
        "author_nationality":  book.author.nationality if book.author else None,
        "created_at":          book.created_at.isoformat() if book.created_at else None,
    }


def index_book(book: models.Book) -> None:
    """Index (or re-index) a single book document."""
    es.index(index=BOOKS_INDEX, id=str(book.id), document=book_to_doc(book))


def remove_book(book_id: int) -> None:
    """Remove a book from the index."""
    try:
        es.delete(index=BOOKS_INDEX, id=str(book_id))
    except NotFoundError:
        pass


def bulk_index_books(books: List[models.Book]) -> int:
    """Bulk-index a list of books. Returns count indexed."""
    from elasticsearch.helpers import bulk

    actions = [
        {
            "_index": BOOKS_INDEX,
            "_id": str(book.id),
            "_source": book_to_doc(book),
        }
        for book in books
    ]
    if not actions:
        return 0
    success, _ = bulk(es, actions)
    return success


# ── AUTHOR INDEXING ───────────────────────────────────────────────────────────

def author_to_doc(author: models.Author) -> Dict[str, Any]:
    """Convert an Author ORM object to an ES document dict."""
    return {
        "id":          author.id,
        "name":        author.name,
        "bio":         author.bio,
        "nationality": author.nationality,
        "created_at":  author.created_at.isoformat() if author.created_at else None,
    }


def index_author(author: models.Author) -> None:
    """Index (or re-index) a single author document."""
    es.index(index=AUTHORS_INDEX, id=str(author.id), document=author_to_doc(author))


def bulk_index_authors(authors: List[models.Author]) -> int:
    """Bulk-index a list of authors. Returns count indexed."""
    from elasticsearch.helpers import bulk

    actions = [
        {
            "_index": AUTHORS_INDEX,
            "_id": str(author.id),
            "_source": author_to_doc(author),
        }
        for author in authors
    ]
    if not actions:
        return 0
    success, _ = bulk(es, actions)
    return success


# ── SEARCH ────────────────────────────────────────────────────────────────────

def search_books(
    query: str,
    genre: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    published_year: Optional[int] = None,
    in_stock: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Full-text search across book title, description, and author name.
    Supports optional filters: genre, price range, published_year, in_stock.
    Returns hits with scores and total count.
    """
    must: List[Dict] = []
    filters: List[Dict] = []

    # Full-text query
    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description^1", "author_name^2"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        })
    else:
        must.append({"match_all": {}})

    # Filters
    if genre:
        filters.append({"term": {"genre": genre}})
    if published_year:
        filters.append({"term": {"published_year": published_year}})
    if in_stock is True:
        filters.append({"range": {"stock": {"gt": 0}}})
    if min_price is not None or max_price is not None:
        price_range: Dict = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        filters.append({"range": {"price": price_range}})

    body = {
        "from": skip,
        "size": limit,
        "query": {
            "bool": {
                "must": must,
                "filter": filters,
            }
        },
        "highlight": {
            "fields": {
                "title":       {"number_of_fragments": 0},
                "description": {"fragment_size": 150, "number_of_fragments": 1},
                "author_name": {"number_of_fragments": 0},
            },
            "pre_tags":  ["<mark>"],
            "post_tags": ["</mark>"],
        },
    }

    response = es.search(index=BOOKS_INDEX, body=body)
    hits = response["hits"]

    results = []
    for hit in hits["hits"]:
        doc = hit["_source"]
        doc["_score"] = hit["_score"]
        doc["_highlight"] = hit.get("highlight", {})
        results.append(doc)

    return {
        "total": hits["total"]["value"],
        "results": results,
    }


def search_authors(
    query: str,
    nationality: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Full-text search across author name and bio.
    Supports optional nationality filter.
    """
    must: List[Dict] = []
    filters: List[Dict] = []

    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["name^3", "bio^1"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        })
    else:
        must.append({"match_all": {}})

    if nationality:
        filters.append({"term": {"nationality": nationality}})

    body = {
        "from": skip,
        "size": limit,
        "query": {
            "bool": {
                "must": must,
                "filter": filters,
            }
        },
        "highlight": {
            "fields": {
                "name": {"number_of_fragments": 0},
                "bio":  {"fragment_size": 150, "number_of_fragments": 1},
            },
            "pre_tags":  ["<mark>"],
            "post_tags": ["</mark>"],
        },
    }

    response = es.search(index=AUTHORS_INDEX, body=body)
    hits = response["hits"]

    results = []
    for hit in hits["hits"]:
        doc = hit["_source"]
        doc["_score"] = hit["_score"]
        doc["_highlight"] = hit.get("highlight", {})
        results.append(doc)

    return {
        "total": hits["total"]["value"],
        "results": results,
    }


def get_search_suggestions(prefix: str, size: int = 5) -> List[str]:
    """
    Autocomplete suggestions for book titles matching a prefix.
    """
    body = {
        "size": size,
        "_source": ["title"],
        "query": {
            "match_phrase_prefix": {
                "title": {"query": prefix, "max_expansions": 20}
            }
        },
    }
    response = es.search(index=BOOKS_INDEX, body=body)
    return [hit["_source"]["title"] for hit in response["hits"]["hits"]]
