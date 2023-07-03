import logging
import dataclasses as dc
import sqlite3
from typing import (
    Self, Generic, TypeVar, Iterable, Optional, Any, Callable
)
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
    def join(self, table: type[Any]) -> Self:
        target_table = orm.sql_table_name(table)
        field = next(
            field for field in dc.fields(self.model) if get_fk_table(field) == target_table
        )
        self.join_clause = _prepare_join(
            source_table=orm.sql_table_name(self.model),
            target_table=target_table,
            source_key=field.name,
            target_key=field.metadata["fk"].key or field.name,
        )
        return self

    def extra(self, *fields: str) -> Self:
        self.extra_columns = list(fields)
        return self

    def where(self, condition: Optional[str] = None, **kwargs) -> Self:
        if condition:
            for key, value in kwargs.items():
                condition = condition.replace(f":{key}", to_sql_literal(value))
            conditions = [condition]
        else:
            table_name = orm.sql_table_name(self.model)
            conditions = []
            for key, value in kwargs.items():
                conditions.append(f"{table_name}.{key} = {to_sql_literal(value)}")

        for condition in conditions:
            if self.where_clause == "":
                self.where_clause = f"WHERE ({condition})"
            else:
                self.where_clause += f" AND ({condition})"

        return self

    def order_by(self, clause: str) -> Self:
        self.order_by_clause = f"ORDER BY {clause}"
        return self

    def limit(self, limit: int) -> Self:
        """
        Applies a sql LIMIT.
        Note that calling this multiple times on the same query, will override the previously set limit.
        """
        self.limit_clause = f"LIMIT {limit}"
        return self

    def _execute(self, db: DbConnection) -> sqlite3.Cursor:
        extra = ""
        if self.extra_columns:
            extra = f",{','.join(self.extra_columns)}"

        table_name = orm.sql_table_name(self.model)
        query = f"""
            SELECT \"{table_name}\".*{extra}
            FROM \"{table_name}\"
            {self.join_clause}
            {self.where_clause}
            {self.order_by_clause}
            {self.limit_clause}
        """
        logger.debug(query)

        return db.execute(query)

    def models(self, db: DbConnection) -> list[Model]:
        cursor = self._execute(db)
        return [self._to_model(row) for row in cursor]

    def dicts(self, db: DbConnection) -> list[dict[str, Any]]:
        rows = []
        cursor = self._execute(db)
        for raw in cursor:
            extra = dict()
            for desc, value in zip(cursor.description, raw):
                key = desc[0]
                extra[key] = value
            rows.append(extra)
        return rows

    def rows(self, db: DbConnection) -> list[Row[Model]]:
        rows = []
        cursor = self._execute(db)
        model_fields = set(field.name for field in dc.fields(self.model))
        for raw in cursor:
            extra = dict()
            model_dict = dict()
            for desc, value in zip(cursor.description, raw):
                key = desc[0]
                if key in model_fields:
                    model_dict[key] = value
                else:
                    extra[key] = value
            rows.append(Row(model=self.model(**model_dict), extra=extra))
        return rows

    def _to_model(self, row: tuple[Any, ...]) -> Model:
        return self.model(*row[: self.model_field_count])



def select(model: type[Model]) -> SelectQuery[Model]:
    """
    Begin a select query.

    :param model: Model class; this determines which model is when binding the sql rows into python objects
    """
    return SelectQuery(model)


def upsert(
    db: DbConnection, records: list[Model], *, update: list[str]
):  # pyright: ignore
    """
    Insert records, on conflict, update fields but only specific ones

    :param db: A sqlite database connection
    :param records: Records to insert or update
    :param update: List of column names to update in case of conflict
    """
    # :param update: List of fields to update in the case of a conflict
    if len(records) == 0:
        return
    model = type(records[0])
    table = orm.sql_table_name(model)
    columns = [field.name for field in dc.fields(model)]
    to_sql: Callable[[Model], str] = lambda row: to_sql_literal([getattr(row, col) for col in columns])

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


def get_fk_table(field: dc.Field[Any]) -> Optional[str]:
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
