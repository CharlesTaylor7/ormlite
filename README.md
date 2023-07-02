# ormlite
Motivation goes here

# Usage

Install:
```
pip install ormlite
```

Sample code:
```python3
from datetime import datetime
from ormlite import connect_to_sqlite, model, select, upsert

@model('persons')
class Person:
  age: int
  height: str
  last_seen: datetime = datetime.now()

db = connect_to_sqlite("demo.db")

upsert(db, [Person(23, "5'10\"")], update=[])

models = select(Person).where("age = '23'").models(db)
assert list(models) == [Person(23, "5'10\"")]

db.close()
```

# TODO
- 100% code coverage
- github actions to check commits and publish to pypi
- Fill out README
- document the api
