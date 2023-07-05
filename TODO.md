# 1.0.0 Release
- Document public api
  - [ ] field
  - [ ] model
  - [ ] Row
  - [ ] SelectQuery

- [x] Distribute ormlite, without packaging the test suite
- [x] BoolAdapter uses integers instead of text. That will interop with existing sqlite tables better

- [x] 100% code coverage
- Workflows:
  - [x] Publish to PyPI
  - [x] pytest
  - [x] pyright


# Future work
- Features:
  - [ ] optionally serialize migrations
  - [ ] interactive migration mode where each operation is approved
  - [ ] migrate applies non destructive changes:
    - add tables and add columns.
    - to delete tables or columns use the `allow_destructive=True` keyword argument
- README badges:
  - [ ] publish to pypi
  - [ ] pyright
  - [ ] pytest

- Dev tools:
  - [ ] linter?
  - [ ] formatter?

- Fixup the sphinx docs. The Readthedocs configuration doesn't work right now
