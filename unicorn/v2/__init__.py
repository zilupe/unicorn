from unicorn.v2.season_page import SeasonPage
from unicorn.v2.storage import store_season_page


def process_season_page(input_file):
    store_season_page(SeasonPage.from_html_file(input_file))

