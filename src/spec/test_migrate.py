import sqlite3
import logging
from typing import Optional
from unittest import mock
from datetime import datetime

from ormlite.orm import model, field
from ormlite.migrate import run


def test_migrate_lifecycle():
    # Arrange: persons table
    @model("persons")
    class Person:
        age: int
        name: str
        funny: bool
        address: Optional[str] = ''
        phone: Optional[int] = None
        subscribed_at: datetime = field(default_factory=datetime.now)

    db = sqlite3.connect(":memory:", isolation_level=None)

    # Act
    run(db)

    # Assert
    rows = db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """).fetchall()

    assert rows == [('persons', 'CREATE TABLE "persons" (\n            age INTEGER NOT NULL,name TEXT NOT NULL,funny BOOL NOT NULL,address TEXT ,phone INTEGER ,subscribed_at TIMESTAMP \n        )')]


    # Arrange: modify persons table
    @model("persons")
    class Person:
        age: int
        name: str
        address: Optional[str] = ''

    # Act
    run(db)

    # Assert
    rows = db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """).fetchall()

    assert rows == [('persons', 'CREATE TABLE "persons" (\n            age INTEGER NOT NULL,name TEXT NOT NULL,address TEXT )')]
