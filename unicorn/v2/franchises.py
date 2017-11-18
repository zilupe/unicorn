import csv
import os.path

from unicorn import unicorn_root_dir
from unicorn.configuration import logging
from unicorn.models import Franchise


log = logging.getLogger(__name__)


def create_franchises():
    with open(os.path.join(unicorn_root_dir, 'unicorn/data/franchises.csv')) as f:
        for row in csv.DictReader(f):
            Franchise.create(
                id=int(row['id']),
                name=row['name'],
                status=row['status'],
            )
