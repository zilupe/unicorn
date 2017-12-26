#!/usr/bin/env bash

set -x
set -e

pytest

python -m unicorn.recreate_db && python -m unicorn.v2.go
python -m unicorn.pages.standard
