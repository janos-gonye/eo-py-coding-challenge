"""
Database models.
"""

import json
import uuid
from datetime import datetime, timezone
from peewee import Model, UUIDField, CharField, DateTimeField, TextField
from public_api.db import db


class JSONField(TextField):
    """Field for storing JSON data in a TextField."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        """Convert the python value for storage in the database."""
        return value if value is None else json.dumps(value)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        return value if value is None else json.loads(value)


class IPCheck(Model):
    """IP validation check record."""

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    ip_address = CharField(index=True)
    verdict = CharField(null=True)
    raw_data = JSONField(null=True)
    task_status = CharField(
        default="pending",
        choices=[
            ("success", "success"),
            ("failed", "failed"),
            ("processing", "processing"),
            ("pending", "pending"),
        ],
    )
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        """Database metadata for Peewee."""

        # pylint: disable=too-few-public-methods
        database = db
        table_name = "ip_checks"


def create_tables():
    """Create all tables in the database."""
    with db:
        db.create_tables([IPCheck])
