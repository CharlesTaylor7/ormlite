import typing
import logging
import dataclasses as dc
import sqlite3
from collections.abc import Sequence
from typing import (
    dataclass_transform,
    final,
    Any,
    Optional,
    Iterable,
    TypeVar,
    ClassVar,
    Generic,
    Protocol,
)
from datetime import datetime, date

from ormlite.utils import cast, get_optional_type_arg

logger = logging.getLogger(__name__)

T = TypeVar("T")

def tap(val: T) -> T:
    print(val)
    return val

class Adapter(Generic[T]):
    sql_name: ClassVar[str]
    python_type: ClassVar[type]

    def convert(self, b: bytes) -> T:
        raise NotImplemented

    def adapt(self, val: T) -> str:
        raise NotImplemented


class DatabaseConnection(Protocol):
    def close(self) -> None:
        ...

    def execute(self, statement: str, **kwargs: Any) -> sqlite3.Cursor:
        ...


@dataclass_transform()
def model(sql_table_name: str):
    if isinstance(sql_table_name, type):
        raise TypeError("@model(sql_table_name) must be called with the sql table name")

    def wrap(cls: type):
        logger.debug(f"applying @model({sql_table_name}) to {cls})")
        # always a dataclass
        cls = dc.dataclass(cls, slots=True)  # pyright: ignore
        _register_model(sql_table_name, cls)
        return cls

    return wrap


@dc.dataclass
class ForeignKey:
    table: str
    key: Optional[str] = None

    def to_constraint(self, field: dc.Field) -> str:
        return (
            f"FOREIGN KEY ({field.name}) "
            f"REFERENCES {self.table}({self.key or field.name})"
        )


def field(*, pk: bool = False, fk: Optional[str] = None, **kwargs: Any):
    foreign_key: Optional[ForeignKey] = None
    if fk:
        parts = fk.split(".")
        if len(parts) > 2:
            raise Exception("invalid fk")
        table = parts[0]
        key = get(parts, 1)
        foreign_key = ForeignKey(table=cast(table, str), key=key)

    return dc.field(
        **kwargs,
        metadata={
            "pk": pk,
            "fk": foreign_key,
        },
    )

def get(seq: Sequence[T], index: int) -> Optional[T]:
    if index >= len(seq):
        return None
    else:
        return seq[index]


# TODO: can we query this info from SQLite's list of converters & adapters?
default_type_mappings = {
    str: "TEXT",
    int: "INTEGER",
    bytes: "BYTES",
    float: "REAL",
    # https://docs.python.org/3/library/sqlite3.html?highlight=sqlite3#default-adapters-and-converters
    bool: "BOOL",
    datetime: "TIMESTAMP",
    date: "DATE",
}


def to_sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"

    if isinstance(value, str):
        # TODO: sqlite escape string contents
        return f"'{value}'"

    # bool is a subtype of int
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value}"

    if isinstance(value, float):
        return f"{value}"

    if isinstance(value, (list, tuple)):
        return f"({','.join(to_sql_literal(item) for item in value)})"

    for adapter in ADAPTERS:
        if isinstance(value, adapter.python_type):
            # TODO: sqlite escape text contents
            # ASSUMPTION: custom adapters always encode to text
            return f"'{adapter.adapt(value)}'"

    raise NotImplementedError


def column_def(field: dc.Field) -> str:
    optional_inner_type = get_optional_type_arg(field.type)

    # not null is applied to all fields automatically
    # use default = None to get a nullable field
    constraint = "NOT NULL"

    if field.metadata.get("pk"):
        constraint = "PRIMARY KEY"

    elif field.default is None or optional_inner_type is not None:
        constraint = ""

    # nullable, since we can't convert a python factory into a sql factory
    elif field.default_factory != dc.MISSING:
        constraint = ""

    elif field.default != dc.MISSING:
        constraint = f"DEFAULT {to_sql_literal(field.default)} NOT NULL"

    field_type = optional_inner_type or field.type
    return f"{field.name} {default_type_mappings[field_type]} {constraint}".strip()


MODEL_TO_TABLE: dict[type, str] = dict()
TABLE_TO_MODEL: dict[str, type] = dict()
ADAPTERS: list[Adapter] = []


def models() -> dict[str, type]:
    return TABLE_TO_MODEL


def adapters() -> Iterable[Adapter]:
    return ADAPTERS

def sql_table_name(model: type) -> str:
    return MODEL_TO_TABLE[model]


def _register_model(sql_table_name: str, model: type):
    if sql_table_name in MODEL_TO_TABLE:
        logger.warning(
            f"Attempt to reregister the sql table '{sql_table_name}' with {model}"
        )
    TABLE_TO_MODEL[sql_table_name] = model
    MODEL_TO_TABLE[model] = sql_table_name

def register_adapter(adapter: Adapter[Any]):
    ADAPTERS.append(adapter)
    sqlite3.register_adapter(adapter.python_type, adapter.adapt)
    sqlite3.register_converter(adapter.sql_name, adapter.convert)
