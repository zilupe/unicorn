#!/usr/bin/env bash

set -x
set -e

flake8
isort

rm -f ./unicorn.db
alembic upgrade head
python -m unicorn.v2.go
python -m unicorn.pages.standard
