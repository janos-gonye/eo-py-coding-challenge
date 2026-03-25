"""
Database connection initialization.
"""

from peewee import SqliteDatabase
from public_api.config import settings

db = SqliteDatabase(
    settings.db_path,
    pragmas={
        # "wal" (Write-Ahead Logging) mode improves concurrency by allowing readers
        # and writers to operate simultaneously without blocking each other.
        "journal_mode": "wal",
        # Negative cache_size specifies the cache size in kilobytes.
        # -1024 * 64 means 64 MB of RAM will be allocated for the SQLite cache.
        "cache_size": -1024 * 64,
    },
    timeout=10,
)
