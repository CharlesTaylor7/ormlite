import typing
from pathlib import Path


T = typing.TypeVar("T")

def get_optional_type_arg(ty: type) -> typing.Optional[type]:
    """
    Gets the inner type of an optional
    """
    origin = typing.get_origin(ty)
    if origin != typing.Union:
        return None

    args = typing.get_args(ty)
    if len(args) != 2:
        return None

    arg = next(arg for arg in args if arg is not None)
    if ty == typing.Optional[arg]:
        return arg
    else:
        return None


def cast(obj: typing.Any, ty: type[T]) -> T:
    if not isinstance(obj, ty):
        raise TypeError

    return obj  # pyright: ignore

def not_null(obj: typing.Optional[T]) -> T:
    if obj is None:
        raise TypeError
    return obj
