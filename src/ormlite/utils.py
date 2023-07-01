import typing


T = typing.TypeVar("T")


def get_optional_type_arg(ty: type) -> typing.Optional[type]:
    """
    Gets the inner type of an optional
    """
    origin = typing.get_origin(ty)
    print("origin", origin)
    if origin != typing.Union:
        return None

    args = typing.get_args(ty)
    print("args", args)
    if len(args) != 2:
        return None

    arg = next(arg for arg in args if arg is not None)
    print("arg", arg)
    if ty == typing.Optional[arg]:
        return arg
    else:
        return None
