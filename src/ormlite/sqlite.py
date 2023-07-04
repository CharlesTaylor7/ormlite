import sqlite3


def connect_to_sqlite(file_name: str) -> sqlite3.Connection:
    """
    Opens a new sqlite connection in Auto-commit mode.

    :param file_name: sqlite database file to open (or create if it doesn't exist yet).
        Use the special argument of ":memory:" to only hold the database in memory and skip writing to file.

    """
    return sqlite3.connect(
        file_name,
        # auto-commit mode
        isolation_level=None,
        # required for adapters to work
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
