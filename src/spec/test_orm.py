import pytest
import dataclasses as dc
import sqlite3
from typing import Union

from ormlite import model, field, migrate
from ormlite.errors import MissingAdapterError
from ormlite.orm import ForeignKey
from .utils import unregister_all_models


def test_bare_model_decorator_is_not_supported():
    with pytest.raises(TypeError):
        @model
        class Foo:
            pass


def test_field_unions_not_supported():
    with pytest.raises(MissingAdapterError):
        @model('union_operator')
        class Foo:
            bar: str | int

    with pytest.raises(MissingAdapterError):
        @model('double_union')
        class Foo:
            bar: Union[str, int]

    with pytest.raises(MissingAdapterError):
        @model('triple_union')
        class Foo:
            bar: Union[str, int, float]

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
    with pytest.raises(Exception):

        @model("foos")
        class Foo:
            fk: field(fk="three.part.fk")
