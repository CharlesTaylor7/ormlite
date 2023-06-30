from datetime import datetime, date

from ormlite import orm
from ormlite.orm import Adapter


def register():
    orm.register_adapter(BoolAdapter())
    orm.register_adapter(DateTimeAdapter())
    orm.register_adapter(DateAdapter())


class BoolAdapter(Adapter[bool]):
    sql_name = "BOOL"

    def convert(self, b: bytes) -> bool:
        if b == b"T":
            return True
        elif b == b"F":
            return False
        else:
            raise Exception

    def adapt(self, val: bool) -> str:
        return "T" if val else "F"


class DateAdapter(Adapter[date]):
    sql_name = "DATE"

    def convert(self, b: bytes) -> date:
        return date.fromisoformat(b.decode())

    def adapt(self, val: date) -> str:
        return val.isoformat()


class DateTimeAdapter(Adapter[datetime]):
    sql_name = "TIMESTAMP"

    def convert(self, b: bytes) -> datetime:
        return datetime.fromisoformat(b.decode())

    def adapt(self, val: datetime) -> str:
        return val.isoformat()
