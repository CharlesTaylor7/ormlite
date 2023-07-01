import sqlite3
import pytest
from typing import Optional
from unittest import mock
from datetime import datetime

from ormlite import model, field, migrate, connect_to_sqlite
from ormlite.migrate import parse_column_names

from .utils import unregister_all_models


def fetch_table_defs(db):
    return db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """
    ).fetchall()


def test_parse_column_names_failed_regex():
    with pytest.raises(Exception, match="regex failed to parse"):
        parse_column_names("Crit TABlE")


def test_migrate_lifecycle():
    # Arrange: persons table
    @model("persons")
    class Person:
        age: int
        name: str
        address: Optional[str] = ""
        phone: Optional[int] = None
        subscribed_at: datetime = field(default_factory=datetime.now)

    db = connect_to_sqlite(":memory:")

    # Act
    migrate(db)

    # Assert
    assert fetch_table_defs(db) == [
        (
            "persons",
            'CREATE TABLE "persons" (age INTEGER NOT NULL, name TEXT NOT NULL, address TEXT, phone INTEGER, subscribed_at TIMESTAMP)',
        )
    ]

    # Arrange: add & remove columns for persons table
    @model("persons")
    class Person:
        age: int
        name: str
        funny: bool
        height: float
        address: Optional[str] = ""
        phone: Optional[int] = None

    # Act
    migrate(db)

    # Assert
    assert fetch_table_defs(db) == [
        (
            "persons",
            'CREATE TABLE "persons" (age INTEGER NOT NULL, name TEXT NOT NULL, address TEXT, phone INTEGER, funny BOOL NOT NULL, height REAL NOT NULL)',
        )
    ]

    # Arrange: delete models
    unregister_all_models()

    # Act
    migrate(db)

    # Assert
    assert fetch_table_defs(db) == []

    db.close()
