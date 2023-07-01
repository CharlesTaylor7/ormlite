import sqlite3


def connect(file_name: str) -> sqlite3.Connection:
    return sqlite3.connect(
        file_name,
        # auto-commit mode
        isolation_level=None,
        # required for adapters to work
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
