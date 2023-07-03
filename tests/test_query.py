import sqlite3
import pytest
from typing import Optional
from unittest import mock
from datetime import datetime, date

from ormlite import model, field, select, upsert, migrate, connect_to_sqlite, Row

from .utils import unregister_all_models


def test_select_tables():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        color_id: int = field(fk="colors.id")
        purchased_at: date = date.today()

    @model("colors")
    class Color:
        id: int = field(pk=True)
        name: str

    db = connect_to_sqlite(":memory:")
    tables = [
        Table(id="dining", legs=4, color_id=2, purchased_at=date(2023, 6, 6)),
        Table(id="patio", legs=5, color_id=3, purchased_at=date(1981, 2, 2)),
        Table(id="stool", legs=3, color_id=1, purchased_at=date(1999, 12, 12)),
    ]
    migrate(db)
    upsert(db, tables, update=[])

    assert select(Table).models(db) == tables
    unregister_all_models()


def test_select__join():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        color_id: int = field(fk="colors.id")
        purchased_at: date = date.today()

    @model("colors")
    class Color:
        id: int = field(pk=True)
        name: str

    db = connect_to_sqlite(":memory:")

    dining = Table(id="dining", legs=4, color_id=2, purchased_at=date(2023, 6, 6))
    patio = Table(id="patio", legs=5, color_id=3, purchased_at=date(1981, 2, 2))
    stool = Table(id="stool", legs=3, color_id=1, purchased_at=date(1999, 12, 12))
    tables = [dining, patio, stool]
    colors = [
        Color(1, "red"),
        Color(2, "green"),
        Color(3, "blue"),
    ]
    migrate(db)
    upsert(db, tables, update=[])
    upsert(db, colors, update=[])

    query = select(Table).join(Color).extra("colors.name AS color")
    rows = query.rows(db)
    assert len(rows) == 3
    assert rows == [Row(dining, extra={"color": "green"}), Row(patio, extra={"color": "blue"}), Row(stool, extra={"color": "red"})]
    unregister_all_models()


def test_where_clause__kwargs():
    @model("foos")
    class Foo:
        a: str
        b: str
        c: str

    records = [
        Foo(a="1", b="2", c="3"),
        Foo(a="4", b="2", c="3"),
        Foo(a="7", b="8", c="3"),
        Foo(a="10", b="2", c="12"),
    ]
    db = connect_to_sqlite(":memory:")
    migrate(db)
    upsert(db, records, update=[])

    assert select(Foo).where(a="1").models(db) == records[:1]
    assert select(Foo).where(b="2").where(c="3").models(db) == records[:2]
    assert select(Foo).where(b="2", c="3").models(db) == records[:2]
    unregister_all_models()


def test_where_clause__interpolation():
    @model("foos")
    class Foo:
        a: int
        b: int
        c: int

    records = [
        Foo(a=1, b=2, c=3),
        Foo(a=4, b=2, c=3),
        Foo(a=7, b=8, c=3),
        Foo(a=10, b=2, c=12),
    ]
    db = connect_to_sqlite(":memory:")
    migrate(db)
    upsert(db, records, update=[])

    assert select(Foo).where("a >= :value", value=7).models(db) == records[2:]
    unregister_all_models()

def test_upsert_empty_list():
    db = None
    records = []
    upsert(db, records, update=[])

def test_upsert_on_conflict():
    @model("foo")
    class Foo:
        id: int = field(pk=True)
        # color: str = field(pk=True)
        a: int
        b: int

    db = connect_to_sqlite(":memory:")
    migrate(db)
    records = [Foo(id=1, a=1, b=1), Foo(id=2, a=2, b=2)]
    upsert(db, records, update=["a"])

    records[0].a = 2
    records[0].b = 2

    upsert(db, records, update=["a"])
    assert select(Foo).where(id=1).models(db) == [Foo(id=1, a=2, b=1)]

    upsert(db, records, update=["a", "b"])
    assert select(Foo).where(id=1).models(db) == [Foo(id=1, a=2, b=2)]


def test_select_limit():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        color_id: int = field(fk="colors.id")
        purchased_at: date = date.today()

    db = connect_to_sqlite(":memory:")
    tables = [
        Table(id="dining", legs=4, color_id=2, purchased_at=date(2023, 6, 6)),
        Table(id="patio", legs=5, color_id=3, purchased_at=date(1981, 2, 2)),
        Table(id="stool", legs=3, color_id=1, purchased_at=date(1999, 12, 12)),
    ]
    migrate(db)
    upsert(db, tables, update=[])

    assert select(Table).limit(3).limit(2).models(db) == tables[:2]
    unregister_all_models()


def test_select_limit():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        purchased_at: date = date.today()

    db = connect_to_sqlite(":memory:")
    tables = [
        Table(id="dining", legs=4, purchased_at=date(2023, 6, 6)),
        Table(id="patio", legs=5, purchased_at=date(1981, 2, 2)),
        Table(id="stool", legs=3, purchased_at=date(1999, 12, 12)),
    ]
    migrate(db)
    upsert(db, tables, update=[])

    assert select(Table).limit(3).limit(2).models(db) == tables[:2]
    unregister_all_models()

def test_select_order_by():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        purchased_at: date = date.today()


    dining = Table(id="dining", legs=4, purchased_at=date(2023, 6, 6))
    patio = Table(id="patio", legs=5, purchased_at=date(1981, 2, 2))
    stool = Table(id="stool", legs=3, purchased_at=date(1999, 12, 12))
    tables = [dining,patio,stool]
    db = connect_to_sqlite(":memory:")
    migrate(db)
    upsert(db, tables, update=[])

    assert select(Table).order_by("legs").models(db) == [stool, dining,patio]
    unregister_all_models()


def test_bool_columns():
    @model("items")
    class Item:
        id: int = field(pk=True)
        round: Optional[bool]
        flat: bool = True
        sharp: bool = False

    db = connect_to_sqlite(":memory:")
    migrate(db)
    db.execute("""
        INSERT INTO items(id, round)
        VALUES (1, 3), (2, NULL), (3, False), (4, True)
    """)

    query = select(Item).where("round")
    assert query.dicts(db) == [
        {'id': 1, 'flat': True, 'round': True, 'sharp': False},
        {'id': 4, 'flat': True, 'round': True, 'sharp': False},
    ]

    unregister_all_models()


def test_datetime_columns():
    @model("items")
    class Item:
        purchased_at: datetime

    records = [
        Item(purchased_at=datetime(2020, 3, 3)),
        Item(purchased_at=datetime(2021, 3, 5)),
    ]

    db = connect_to_sqlite(":memory:")
    migrate(db)
    upsert(db, records, update=[])

    assert select(Item).models(db) == records
    unregister_all_models()


