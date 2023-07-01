import sqlite3
import pytest
from typing import Optional
from unittest import mock
from datetime import datetime

from ormlite import model, field, select, upsert, migrate

from .utils import unregister_all_models


def test_select_tables():
    @model("tables")
    class Table:
        id: str = field(pk=True)
        legs: int
        color_id: int = field(fk="colors.id")

    @model("colors")
    class Color:
        id: int = field(pk=True)
        name: str

    db = sqlite3.connect(":memory:", isolation_level=None)
    migrate(db)
    upsert(
        db,
        [
            Table(id="stool", legs=3, color_id=1),
            Table(id="dining", legs=4, color_id=2),
            Table(id="patio", legs=5, color_id=3),
        ],
        update=[],
    )

    assert list(select(Table).models(db)) == [
        Table(id="dining", legs=4, color_id=2),
        Table(id="patio", legs=5, color_id=3),
        Table(id="stool", legs=3, color_id=1),
    ]
    unregister_all_models()
