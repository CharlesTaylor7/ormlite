import typing


T = typing.TypeVar("T")

# because typing.types.UnionType is not publicly exported 
UNION_TYPE = typing.get_origin(str | float)


def get_optional_type_arg(ty: type) -> typing.Optional[type]:
    """
    Gets the inner type of an optional
    """
    origin = typing.get_origin(ty)
    if origin != typing.Union and origin != UNION_TYPE:
        return None

    args = typing.get_args(ty)
    if len(args) != 2:
        return None

    arg = next(arg for arg in args if arg is not None)
    if ty == typing.Optional[arg]:
        return arg
    else:
        return None
