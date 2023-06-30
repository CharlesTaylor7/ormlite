from typing import Optional
from datetime import datetime, date

from ormlite import orm
from ormlite.orm import Adapter


def register():
    orm.register_adapter(BoolAdapter())
    orm.register_adapter(DateTimeAdapter())
    orm.register_adapter(DateAdapter())


class BoolAdapter(Adapter[bool]):
    sql_name = "BOOL"
    python_type = bool

    def convert(self, b: bytes) -> Optional[bool]:
        if b == b"T":
            return True
        elif b == b"F":
            return False
        else:
            raise Exception

    def adapt(self, boolean: Optional[bool]):
        if boolean is None:
            return None
        else:
            return "T" if boolean else "F"


class DateAdapter(Adapter[date]):
    sql_name = "DATE"
    python_type = date

    def convert(self, b: bytes) -> date:
        return date.fromisoformat(b.decode())

    def adapt(self, val: date) -> str:
        return val.isoformat()


class DateTimeAdapter(Adapter[datetime]):
    sql_name = "TIMESTAMP"
    python_type = datetime

    def convert(self, b: bytes) -> date:
        return datetime.fromisoformat(b.decode())

    def adapt(self, val):
        return val.isoformat()
