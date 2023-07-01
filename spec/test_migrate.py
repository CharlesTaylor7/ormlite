import sqlite3
import logging
from typing import Optional
from unittest import mock
from datetime import datetime

from ormlite.orm import model
from ormlite.migrate import run


def test_migrate_new_model():
    # Arrange
    @model
    class Person:
        age: int
        name: str
        funny: bool
        address: Optional[str] = ''
        phone: Optional[int] = None
        subscribed_at: datetime = datetime.now()

    db = sqlite3.connect(":memory:", isolation_level=None)
    # db = mock.Mock(wraps=db)

    # Act
    run(db)

    # Assert
    print(db.call_args_list)

    rows = db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """).fetchall()

    assert rows == None
