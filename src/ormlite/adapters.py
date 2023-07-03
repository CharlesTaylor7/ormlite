import logging
from datetime import datetime, date

from ormlite import orm
from ormlite.orm import Adapter

logger = logging.getLogger(__name__)


def register():
    orm.register_adapter(BoolAdapter())
    orm.register_adapter(DateTimeAdapter())
    orm.register_adapter(DateAdapter())


class BoolAdapter(Adapter[bool]):
    sql_type = "BOOLEAN"
    python_type = bool

    def convert(self, b: bytes) -> bool:
        if b == b"1":
            return True
        elif b == b"0":
            return False
        else:
            logger.warning(f"adapting invalid bool with value of: {b}")
            return True

    def adapt(self, val: bool) -> str:
        return "1" if val else "0"


class DateAdapter(Adapter[date]):
    sql_type = "DATE"
    python_type = date

    def convert(self, b: bytes) -> date:
        return date.fromisoformat(b.decode())

    def adapt(self, val: date) -> str:
        return val.isoformat()


class DateTimeAdapter(Adapter[datetime]):
    sql_type = "TIMESTAMP"
    python_type = datetime

    def convert(self, b: bytes) -> datetime:
        return datetime.fromisoformat(b.decode())

    def adapt(self, val: datetime) -> str:
        return val.isoformat()
