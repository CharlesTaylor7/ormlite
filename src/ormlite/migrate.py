import re
import dataclasses as dc
import logging
from typing import Any, Callable
from collections.abc import Sequence

from ormlite import orm
from ormlite.orm import column_def, DatabaseConnection


logger = logging.getLogger(__name__)


# ASSUMPTIONS:
# - This only handles forward migrations, migrations are not reversible
# - Done: add columns
# - Done: drop columns
# - Done: create tables
# - Done: drop tables
# - Renaming columns or tables can be done with manual sql at the cli
# changing constraints, is a tricky multi step process:
# https://sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes
def migrate(db: DatabaseConnection):
    db.execute("""BEGIN EXCLUSIVE TRANSACTION""")
    cursor = db.execute(
        """
        SELECT tbl_name, sql
        FROM sqlite_schema
        WHERE type = 'table'
    """
    ).fetchall()
    sql_table_defs = {row[0]: row[1] for row in cursor}

    # create new tables
    for table_name, model in orm.models().items():
        if table_name not in sql_table_defs:
            create_table(db, model)

    for table_name, sql in sql_table_defs.items():
        # drop tables
        if table_name not in orm.models():
            drop_table(db, table_name)
            continue

        # migrate columns for existing tables
        fields = dc.fields(orm.models()[table_name])

        field_names = {field.name for field in fields}
        column_names = parse_column_names(sql)

        fields_dict = {field.name: field for field in fields}

        new_fields = field_names - column_names
        new_fields = sorted(new_fields, key=lambda x: index_of(fields, x))

        for field_name in new_fields:
            column = column_def(fields_dict[field_name])
            logger.info(f"Add column for {table_name}: {column}")
            db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column}")

        old_columns = column_names - field_names
        for column_name in old_columns:
            logger.info(f"Drop column for {table_name}: {column_name}")
            db.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

    db.execute("""END TRANSACTION""")


REGEX = re.compile(r'CREATE TABLE "?(?P<table_name>\w+)"?\s*\((?P<defs>[\s\w,\'\(\)]*)')
IDENT = re.compile(r"[a-z]\w*")


def parse_column_names(raw_table_sql: str) -> set[str]:
    match = REGEX.match(raw_table_sql)
    if match is None:
        raise Exception(f"regex failed to parse: {raw_table_sql}")

    defs = match.group("defs").strip().split(",")
    get_name: Callable[[str], str] = lambda row: re.split(r"\s+", row.strip())[0]
    col_names = {
        name for row in defs for name in [get_name(row)] if IDENT.fullmatch(name)
    }
    return col_names


def index_of(fields: Sequence[dc.Field[Any]], name: str) -> int:
    return next(i for i, f in enumerate(fields) if f.name == name)


def create_table(db: DatabaseConnection, model: type):
    defs = (column_def(field) for field in dc.fields(model))
    without_row_id = (
        "WITHOUT ROWID"
        if any(field.metadata.get("pk") for field in dc.fields(model))
        else ""
    )
    name = orm.sql_table_name(model)
    sql_constraints = getattr(model, "sql_constraints", [])

    db.execute(
        f"""
        CREATE TABLE "{name}" ({", ".join([*defs, *fk_constraints(model), *sql_constraints])}) {without_row_id}
        """
    )
    logger.info(f"Table created: {name}")


def fk_constraints(model: type):
    return (
        fk.to_constraint(field)
        for field in dc.fields(model)
        for fk in [field.metadata.get("fk")]
        if fk is not None
    )


def drop_table(db: DatabaseConnection, table_name: str):
    db.execute(
        f"""
        DROP TABLE {table_name}
        """,
    )
    logger.info(f"Table dropped: {table_name}")
