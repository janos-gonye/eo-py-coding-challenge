"""
Shared pytest fixtures and configuration.
"""

import pytest
from public_api.models import IPCheck
from public_api.db import db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup test database using the app db."""
    db.connect(reuse_if_open=True)
    db.create_tables([IPCheck])
    yield
    db.drop_tables([IPCheck])
    db.close()
