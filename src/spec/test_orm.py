import pytest
import dataclasses as dc

from ormlite import model, field
from .utils import unregister_all_models

def test_bare_model_decorator_is_not_supported():
    with pytest.raises(Exception):
        @model
        class Foo:
            pass

def test_foreign_key_punning():
    @model('foos')
    class Foo:
        fk: str = field(fk="bars")

    @model('bars')
    class Foo:
        fk: str

    assert dc.fields(Foo) = []

def test_invalid_foreign_key():
    with pytest.raises(Exception):
        @model('foos')
        class Foo:
            fk: field(fk="three.part.fk")
