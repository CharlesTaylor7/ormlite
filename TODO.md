# 1.0.0 Release
- breaking changes:
  - [ ] migrate applies non destructive changes:
    - add tables and add columns.
    - to delete tables or columns use the `allow_destructive=True` keyword argument
  - [ ] BoolAdapter uses integers instead of text. That will interop with existing sqlite tables better

- [ ] 100% code coverage
- Document public api
  - Code
    - [ ] ormlite
    - [ ] ormlite.errors
  - [ ] Extract code docs to README
- [ ] Distribute ormlite, without packaging the test suite

- Workflows:
  - [x] Publish to PyPI
  - [x] pytest
  - [x] pyright


# Future work
- Features:
  - [ ] optionally serialize migrations
  - [ ] interactive migration mode where each operation is approved

- README badges:
  - [ ] publish to pypi
  - [ ] pyright
  - [ ] pytest

- Dev tools:
  - [ ] linter?
  - [ ] formatter?

- Fixup the sphinx docs. The Readthedocs configuration doesn't work right now
