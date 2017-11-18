import os.path

from unicorn import unicorn_root_dir
from unicorn.app import run_in_app_context
from unicorn.configuration import logging
from unicorn.v2 import process_season_page

source_dir = os.path.join(unicorn_root_dir, 'input/season-pages')


log = logging.getLogger(__name__)


def get_season_page_filenames():
    for filename in os.listdir(source_dir):
        if filename.endswith('.htm'):
            yield os.path.join(source_dir, filename)


@run_in_app_context
def main():
    for filename in get_season_page_filenames():
        log.info('Parsing {}'.format(filename))
        process_season_page(filename)


if __name__ == '__main__':
    main()
