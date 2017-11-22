import os.path

from unicorn import unicorn_root_dir
from unicorn.app import run_in_app_context
from unicorn.configuration import logging
from unicorn.db.base import Session
from unicorn.models import Season
from unicorn.v2 import process_season_page
from unicorn.v2.franchises import create_franchises

source_dir = os.path.join(unicorn_root_dir, 'input/season-pages')


log = logging.getLogger(__name__)


def get_season_page_filenames():
    for filename in os.listdir(source_dir):
        if filename.endswith('.htm'):
            yield os.path.join(source_dir, filename)


@run_in_app_context
def main():
    create_franchises()

    for filename in get_season_page_filenames():
        log.info('Parsing {}'.format(filename))
        process_season_page(filename)

    # Assign season numbers
    for i, season in enumerate(Season.get_all(order_by=[Season.first_week_date.asc()])):
        season.number = '{:02}'.format(i + 1)
        Session.commit()


if __name__ == '__main__':
    main()
