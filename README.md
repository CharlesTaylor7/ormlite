[Read The Docs](https://ormlite.readthedocs.io/en/latest/)

[PyPI](https://pypi.org/project/ormlite)
<!---
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
--->

# Usage

Install:
```
pip install ormlite
```

Sample code:
```python3
from datetime import datetime
from ormlite import connect_to_sqlite, migrate, model, field, select, upsert

@model('persons')
class Person:
  email: str = field(pk=True)
  age: int
  height: str
  last_seen: datetime = datetime.now()

db = connect_to_sqlite("demo.db")
migrate(db)

upsert(db, [Person('me@me.com', 23, "5ft 10in")], update=[])
models = select(Person).where("age = '23'").models(db)
print(list(models))
# Output: [Person(email='me@me.com', age=23, height='5ft 10in', last_seen=datetime.datetime(...))]

db.close()
```


# Motivation
I wanted to query a sqlite database, without writing verbose queries. Previously, for work, I've used django's orm for interacting with sql databases. But for a recent small personal project, I wanted a library to interact with sqlite without depending on an entire web framework.

After I deciding to build my own library, I decided to embrace modern python idioms. So my library is built on top of the dataclasses library in the standard lib. 

To keep scope small, ormlite only interops with sqlite, not other sql databases.

# Use case

ormlite operates off the principle, that your python source code is the source of truth for the state of the sql tables. Migrations are run in a single step, it checks for differences between your python tables and your sql database. Then it applies sql migrations immediately.

Django & Ruby on Rails, have a separate step whereby migrations are serialized to files. Migrations are thus shared across dev machines, and to production this way. 

Since ormlite doesn't do this, it's not suitable for production deployment or teams of devs.

My use case for the library involves running scripts on my local machine, so I enjoy not dealing with the hassle of an evergrowing list of migrations in my repo.
