"""
Elasticsearch client configuration.
Connects to a local ES instance by default.
Override ES_URL via environment variable for production.
"""
import os
from elasticsearch import Elasticsearch

ES_URL = os.getenv("ES_URL", "http://localhost:9200")

es = Elasticsearch(ES_URL)

BOOKS_INDEX = "books"
AUTHORS_INDEX = "authors"


def create_indices():
    """Create ES indices with proper mappings if they don't exist."""

    books_mapping = {
        "mappings": {
            "properties": {
                "id":             {"type": "integer"},
                "title":          {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                "isbn":           {"type": "keyword"},
                "genre":          {"type": "keyword"},
                "description":    {"type": "text", "analyzer": "english"},
                "price":          {"type": "float"},
                "stock":          {"type": "integer"},
                "cover_url":      {"type": "keyword", "index": False},
                "published_year": {"type": "integer"},
                "author_id":      {"type": "integer"},
                "author_name":    {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "author_nationality": {"type": "keyword"},
                "created_at":     {"type": "date"},
            }
        }
    }

    authors_mapping = {
        "mappings": {
            "properties": {
                "id":          {"type": "integer"},
                "name":        {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                "bio":         {"type": "text", "analyzer": "english"},
                "nationality": {"type": "keyword"},
                "created_at":  {"type": "date"},
            }
        }
    }

    if not es.indices.exists(index=BOOKS_INDEX):
        es.indices.create(index=BOOKS_INDEX, body=books_mapping)
        print(f"✅ Created '{BOOKS_INDEX}' index")

    if not es.indices.exists(index=AUTHORS_INDEX):
        es.indices.create(index=AUTHORS_INDEX, body=authors_mapping)
        print(f"✅ Created '{AUTHORS_INDEX}' index")


def check_connection() -> bool:
    """Return True if Elasticsearch is reachable."""
    try:
        return es.ping()
    except Exception:
        return False
