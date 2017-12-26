from unicorn.v2.season_page import SeasonParse
from unicorn.v2.storage import store_season_page


def process_season(standings_file, fixtures_file=None):
    season_parse = SeasonParse()

    with open(standings_file) as f:
        season_parse.parse_standings_page(f.read())

    if fixtures_file:
        with open(fixtures_file) as f:
            season_parse.parse_fixtures_page(f.read())

    store_season_page(season_parse)
