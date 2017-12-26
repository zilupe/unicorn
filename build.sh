#!/usr/bin/env bash

set -x
set -e

pytest

alembic downgrade 0001
alembic upgrade head
python -m unicorn.v2.go
python -m unicorn.pages.standard
