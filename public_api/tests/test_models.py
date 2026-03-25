"""
Unit tests for the database models.
"""

import uuid
from datetime import datetime, timezone

from public_api.models import JSONField, IPCheck, create_tables
from public_api.db import db


def test_json_field_serialization():
    """Test JSONField serialization and deserialization."""
    field = JSONField()
    data = {"key": "value", "list": [1, 2, 3]}

    serialized = field.db_value(data)
    assert isinstance(serialized, str)
    assert '"key": "value"' in serialized

    deserialized = field.python_value(serialized)
    assert deserialized == data

    assert field.python_value(None) is None


def test_ip_check_model_defaults():
    """Test IPCheck model default values."""
    ip_addr = "192.168.1.1"
    check = IPCheck.create(ip_address=ip_addr)

    assert isinstance(check.id, uuid.UUID)
    assert check.ip_address == ip_addr
    assert check.verdict is None
    assert check.raw_data is None
    assert check.task_status == "pending"
    assert isinstance(check.created_at, datetime)
    assert check.created_at.tzinfo == timezone.utc  # pylint: disable=no-member


def test_ip_check_task_status_choices():
    """Test IPCheck task status field constraints (choices)."""
    for status in ["success", "failed", "processing", "pending"]:
        check = IPCheck.create(ip_address="1.1.1.1", task_status=status)
        assert check.task_status == status


def test_create_tables():
    """Test create_tables function."""
    db.drop_tables([IPCheck])

    assert not db.table_exists("ip_checks")

    create_tables()

    assert db.table_exists("ip_checks")
