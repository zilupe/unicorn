import os.path

from unicorn import unicorn_root_dir
from unicorn.app import app
from unicorn.configuration import logging
from unicorn.models import Season
from unicorn.v2 import process_season
from unicorn.v2.franchises import create_franchises

input_dir = os.path.join(unicorn_root_dir, 'input')
source_dir = os.path.join(input_dir, 'season-pages')


log = logging.getLogger(__name__)


def get_season_page_filenames():
    for filename in os.listdir(source_dir):
        if filename.endswith('.htm'):
            yield os.path.join(source_dir, filename)


def main():
    create_franchises()

    for filename in get_season_page_filenames():
        process_season(
            standings_file=filename
        )

    # Current season
    process_season(
        standings_file=os.path.join(input_dir, 'current-season/standings.htm'),
        fixtures_file=os.path.join(input_dir, 'current-season/fixtures.htm'),
    )

    # Assign season numbers
    for i, season in enumerate(Season.get_all(order_by=[Season.first_week_date.asc()])):
        season.number = '{:02}'.format(i + 1)
        app.db_session.commit()


if __name__ == '__main__':
    with app():
        main()
