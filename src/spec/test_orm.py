import pytest

from ormlite import model

def test_bare_model_decorator_is_not_supported():
    with pytest.raises(Exception):
        @model
        class Foo:
            pass
