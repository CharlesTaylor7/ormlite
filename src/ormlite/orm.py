import logging
import dataclasses as dc
import sqlite3
from collections.abc import Sequence
from typing import (
    dataclass_transform,
    Any,
    Optional,
    TypeVar,
    ClassVar,
    Generic,
    Protocol,
)

from ormlite.errors import (
    MissingAdapterError,
    InvalidForeignKeyError,
    MultiplePrimaryKeysError,
)
from ormlite.utils import get_optional_type_arg

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Adapter(Generic[T]):
    sql_type: ClassVar[str]
    python_type: ClassVar[type]

    def convert(self, b: bytes) -> T:
        ...  # pragma: no cover

    def adapt(self, val: T) -> str:
        ...  # pragma: no cover


class DatabaseConnection(Protocol):
    def close(self) -> None:
        ...  # pragma: no cover

    def execute(self, statement: str, **kwargs: Any) -> sqlite3.Cursor:
        ...  # pragma: no cover


class Context:
    ADAPTERS: dict[type, Adapter] = dict()
    PYTHON_TO_SQL_MAPPING: dict[type, str] = dict()

    MODEL_TO_TABLE: dict[type, str] = dict()
    TABLE_TO_MODEL: dict[str, type] = dict()

    @classmethod
    def setup(cls):
        cls.PYTHON_TO_SQL_MAPPING = cls.python_to_sql_mapping()

    @classmethod
    def python_to_sql_mapping(cls) -> dict[type, str]:
        mapping = {
            bytes: "BLOB",
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
        }
        for adapter in cls.ADAPTERS.values():
            mapping[adapter.python_type] = adapter.sql_type
        return mapping


@dataclass_transform()
def model(sql_table_name: str):
    if isinstance(sql_table_name, type):
        raise TypeError("@model(sql_table_name) must be called with the sql table name")

    def wrap(model: type) -> type:
        if sql_table_name in Context.TABLE_TO_MODEL:
            logger.warning(
                f"Reregistering the sql table '{sql_table_name}' with {model}"
            )
        else:
            logger.debug(f"applying @model({sql_table_name}) to {model})")

        model = dc.dataclass(model, slots=True)  # pyright: ignore
        validate_model(model)

        Context.TABLE_TO_MODEL[sql_table_name] = model
        Context.MODEL_TO_TABLE[model] = sql_table_name

        return model

    return wrap


def validate_model(model: type):
    has_primary = False
    for field in dc.fields(model):
        to_sql_type(field.type)

        if field.metadata.get("pk"):
            if has_primary:
                raise MultiplePrimaryKeysError
            else:
                has_primary = True


@dc.dataclass
class ForeignKey:
    table: str
    key: Optional[str] = None

    def to_constraint(self, field: dc.Field[Any]) -> str:
        return (
            f"FOREIGN KEY ({field.name}) "
            f"REFERENCES {self.table}({self.key or field.name})"
        )


def field(*, pk: bool = False, fk: Optional[str] = None, **kwargs: Any):
    foreign_key: Optional[ForeignKey] = None
    if fk:
        parts = fk.split(".")
        if len(parts) > 2:
            raise InvalidForeignKeyError

        table = parts[0]
        key = get(parts, 1)
        foreign_key = ForeignKey(table=(table), key=key)

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

    adapter = Context.ADAPTERS.get(type(value))
    if adapter:
        # TODO: sqlite escape text contents
        # ASSUMPTION: custom adapters always encode to text
        return f"'{adapter.adapt(value)}'"

    raise MissingAdapterError


def to_sql_type(field: type) -> str:
    python_type = get_optional_type_arg(field) or field
    sql_type = Context.PYTHON_TO_SQL_MAPPING.get(python_type)

    if sql_type is not None:
        return sql_type

    raise MissingAdapterError


def column_def(field: dc.Field[Any]) -> str:
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

    return f"{field.name} {to_sql_type(field.type)} {constraint}".strip()


def models() -> dict[str, type]:
    return Context.TABLE_TO_MODEL


def sql_table_name(model: type) -> str:
    return Context.MODEL_TO_TABLE[model]


def register_adapter(adapter: Adapter[Any]):
    Context.ADAPTERS[adapter.python_type] = adapter
    sqlite3.register_adapter(adapter.python_type, adapter.adapt)
    sqlite3.register_converter(adapter.sql_type, adapter.convert)
