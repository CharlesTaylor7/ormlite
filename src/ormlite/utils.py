import typing


T = typing.TypeVar("T")


def get_optional_type_arg(ty: type) -> typing.Optional[type]:
    """
    Gets the inner type of an optional
    """
    origin = typing.get_origin(ty)
    if origin != typing.Union and origin != typing.types.UnionType:
        return None

    args = typing.get_args(ty)
    if len(args) != 2:
        return None

    arg = next(arg for arg in args if arg is not None)
    if ty == typing.Optional[arg]:
        return arg
    else:
        return None
