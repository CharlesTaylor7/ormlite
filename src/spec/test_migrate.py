import sqlite3
from typing import Optional
from unittest import mock
from datetime import datetime

from ormlite.orm import model, field
from ormlite.migrate import run


def fetch_table_defs(db):
    return db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """
    ).fetchall()


def unregister_all_models():
    """
    For testing only
    """
    from ormlite import orm

    orm.MODEL_TO_TABLE = dict()
    orm.TABLE_TO_MODEL = dict()


def test_migrate_lifecycle():
    # Arrange: persons table
    @model("persons")
    class Person:
        age: int
        name: str
        address: Optional[str] = ""
        phone: Optional[int] = None
        subscribed_at: datetime = field(default_factory=datetime.now)

    db = sqlite3.connect(":memory:", isolation_level=None)

    # Act
    run(db)

    # Assert
    assert fetch_table_defs(db) == [
        (
            "persons",
            'CREATE TABLE "persons" (age INTEGER NOT NULL, name TEXT NOT NULL, address TEXT, phone INTEGER, subscribed_at TIMESTAMP)',
        )
    ]

    # Arrange: add columns for persons table
    @model("persons")
    class Person:
        age: int
        name: str
        funny: bool
        address: Optional[str] = ""
        phone: Optional[int] = None
        subscribed_at: datetime = field(default_factory=datetime.now)

    # Act
    run(db)

    # Assert
    assert fetch_table_defs(db) == [
        (
            "persons",
            'CREATE TABLE "persons" (age INTEGER NOT NULL, name TEXT NOT NULL, address TEXT, phone INTEGER, subscribed_at TIMESTAMP, funny BOOL NOT NULL)',
        )
    ]

    # Arrange: remove columns from persons table
    @model("persons")
    class Person:
        age: int
        name: str
        address: Optional[str] = ""

    # Act
    run(db)

    # Assert
    assert fetch_table_defs(db) == [
        (
            "persons",
            'CREATE TABLE "persons" (age INTEGER NOT NULL, name TEXT NOT NULL, address TEXT)',
        )
    ]

    # Arrange: delete models
    unregister_all_models()

    # Act
    run(db)

    # Assert
    assert fetch_table_defs(db) == []
