import logging
import dataclasses as dc
import sqlite3
from typing import Self, Generic, TypeVar, Iterable, Optional
from dataclasses import dataclass

from ormlite import orm
from ormlite.orm import to_sql_literal, DatabaseConnection as DbConnection

logger = logging.getLogger(__name__)


Model = TypeVar("Model")


@dataclass
class Row(Generic[Model]):
    model: Model
    extra: dict


class SelectQuery(Generic[Model]):
    db: DbConnection
    model: type
    join_clause = ""
    where_clause = ""
    order_by_clause = ""
    limit_clause = ""

    def __init__(self, model: type[Model]):
        self.model = model
        self.model_field_count = len(dc.fields(self.model))
        self.extra_columns = []

    # TODO: allow multiple joins via join dict ala ruby on rails
    # allow multiple calls to join
    def join(self, table: str) -> Self:
        field = next(
            field for field in dc.fields(self.model) if get_fk_table(field) == table
        )
        self.join_clause = _prepare_join(
            source_table=orm.sql_table_name(self.model),
            target_table=table,
            source_key=field.name,
            target_key=field.metadata["fk"].key or field.name,
        )
        return self

    def extra(self, *fields: str) -> Self:
        self.extra_columns = list(fields)
        return self

    def where(self, clause: str) -> Self:
        if self.where_clause == "":
            self.where_clause = f"WHERE {clause}"
        else:
            self.where_clause += f" AND ({clause})"

        return self

    def order_by(self, clause: str) -> Self:
        self.order_by_clause = f"ORDER BY {clause}"
        return self

    def limit(self, limit: int) -> Self:
        self.limit_clause = f"LIMIT {limit}"
        return self

    def _execute(self, db: DbConnection) -> sqlite3.Cursor:
        extra = ""
        if self.extra_columns:
            extra = f",{','.join(self.extra_columns)}"

        table_name = orm.sql_table_name(self.model)
        query = f"""
            SELECT {table_name}.*{extra}
            FROM {table_name}
            {self.join_clause}
            {self.where_clause}
            {self.order_by_clause}
            {self.limit_clause}
        """
        logger.debug(query)

        return db.execute(query)

    def models(self, db: DbConnection) -> Iterable[Model]:
        cursor = self._execute(db)
        return (self._to_model(row) for row in cursor)

    def rows(self, db: DbConnection) -> Iterable[Row[Model]]:
        cursor = self._execute(db)
        return (
            Row(
                model=self._to_model(row),
                extra=self._to_extra(row),
            )
            for row in cursor
        )

    def _to_model(self, row: tuple):
        return self.model(*row[: self.model_field_count])

    def _to_extra(self, row: tuple):
        extra = {}
        rest = row[self.model_field_count :]
        for name, value in zip(self.extra_columns, rest):
            extra[name] = value
        return extra


def select(model: type[Model]) -> SelectQuery[Model]:
    return SelectQuery(model)


def upsert(db: DbConnection, records: list[Model], *, update: list[str]): # pyright: ignore
    """
    Insert records, on conflict, update fields but only specific ones
    """
    if len(records) == 0:
        return
    model = type(records[0])
    print(model, hash(model), "upsert")
    table = orm.sql_table_name(model)
    columns = [field.name for field in dc.fields(model)]
    to_sql = lambda row: to_sql_literal([getattr(row, col) for col in columns])

    on_conflict_clause = ""
    if len(update) > 0:
        on_conflict_clause = f"""
            ON CONFLICT DO UPDATE
            SET {','.join(f'{col}=excluded.{col}' for col in update)}
        """

    db.execute(
        f"""
        INSERT INTO {table}({','.join(columns)})
        VALUES {','.join(to_sql(row) for row in records)}
        {on_conflict_clause}
        """
    )


def get_fk_table(field: dc.Field) -> Optional[str]:
    fk = field.metadata.get("fk")
    if not fk:
        return None
    return fk.table


def _prepare_join(
    *,
    source_table: str,
    source_key: str,
    target_table: str,
    target_key: str,
) -> str:
    return f"""
        JOIN {target_table}
        ON {target_table}.{target_key} = {source_table}.{source_key}
    """
