import sqlite3
import pytest
from typing import Optional
from unittest import mock
from datetime import datetime, date

from ormlite import model, field, select, upsert, migrate

from .utils import unregister_all_models

from ormlite.orm import Context

def test_select_tables():
    unregister_all_models()
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
    print(Table, hash(Table), Table.sql_table_name, "after def")
    print(Color, hash(Color), Color.sql_table_name, "after def")
    return

    db = sqlite3.connect(
        ":memory:",
        isolation_level=None,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    tables = [
        Table(id="dining", legs=4, color_id=2, purchased_at=date(2023, 6, 6)),
        Table(id="patio", legs=5, color_id=3, purchased_at=date(1981, 2, 2)),
        Table(id="stool", legs=3, color_id=1, purchased_at=date(1999, 12, 12)),
    ]
    migrate(db)
    upsert(db, tables, update=[])

    assert list(select(Table).models(db)) == tables
    unregister_all_models()
