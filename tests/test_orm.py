import pytest
import dataclasses as dc
import sqlite3
from datetime import datetime, date
from typing import Union, Optional

from ormlite import model, field, migrate
from ormlite.errors import MissingAdapterError, InvalidForeignKeyError, MultiplePrimaryKeysError
from ormlite.orm import ForeignKey, to_sql_literal, to_sql_type
from .utils import unregister_all_models


def test_bare_model_decorator_is_not_supported():
    with pytest.raises(TypeError):
        @model
        class Foo:
            pass


def test_field_optional_union_supported():
    @model("union_operator")
    class Foo:
        bar: str | None

    field = dc.fields(Foo)[0]
    assert field.name == 'bar'
    assert field.type == Optional[str]
    assert to_sql_type(field.type) == "TEXT"


def test_field_unions_not_supported():
    with pytest.raises(MissingAdapterError):

        @model("union_operator")
        class Foo:
            bar: str | int

    with pytest.raises(MissingAdapterError):

        @model("double_union")
        class Foo:
            bar: Union[str, int]

    with pytest.raises(MissingAdapterError):

        @model("triple_union")
        class Foo:
            bar: Union[str, int, float]


def test_multiple_primary_keys():
    with pytest.raises(MultiplePrimaryKeysError):
        @model("items")
        class Item:
            id_1: int = field(pk=True)
            id_2: str = field(pk=True)



def test_foreign_key_punning():
    @model("foos")
    class Foo:
        fk: str = field(fk="bars")

    @model("bars")
    class Bar:
        fk: str

    fields = dc.fields(Foo)
    assert len(fields) == 1
    assert fields[0].metadata["fk"] == ForeignKey(table="bars")


def test_foreign_key_qualified():
    @model("foos")
    class Foo:
        fk: str = field(fk="bars.id")

    @model("bars")
    class Bar:
        id: str = field(pk=True)

    fields = dc.fields(Foo)
    assert len(fields) == 1
    assert fields[0].metadata["fk"] == ForeignKey(table="bars", key="id")


def test_foreign_key_invalid():
    with pytest.raises(InvalidForeignKeyError):

        @model("foos")
        class Foo:
            fk: field(fk="three.part.fk")


def test_to_sql_literal__missing_adapter():
    class Foo:
        pass

    with pytest.raises(MissingAdapterError):
        to_sql_literal(Foo())


def test_to_sql_literal__none():
    assert to_sql_literal(None) == "NULL"


def test_to_sql_literal__float():
    assert to_sql_literal(3.14) == "3.14"


def test_to_sql_literal__date():
    assert to_sql_literal(date(2020, 3, 16)) == "'2020-03-16'"


def test_to_sql_literal__date():
    assert to_sql_literal(datetime(2020, 3, 16)) == "'2020-03-16T00:00:00'"
