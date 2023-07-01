import pytest

from ormlite import model, field

def test_bare_model_decorator_is_not_supported():
    with pytest.raises(Exception):
        @model
        class Foo:
            pass

def test_invalid_foreign_key():
    with pytest.raises(Exception):
        @model('foos')
        class Foo:
            fk: field(fk="three.part.fk")
