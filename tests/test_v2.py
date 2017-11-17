import datetime as dt
import os.path

from unicorn import unicorn_root_dir
from unicorn.models import Season, Team, Game
from unicorn.v2 import process_season_page


def test_processes_autumn_2014_season_page(db):
    assert Season.get_count() == 0
    assert Team.get_count() == 0
    assert Game.get_count() == 0

    input_file = os.path.join(unicorn_root_dir, 'input/season-pages/2014-Autumn.htm')
    assert os.path.isfile(input_file)

    process_season_page(input_file)

    assert Season.get_count() == 1

    season = Season.get_all()[0]
    assert season.id == 55
    assert season.name == 'Autumn 2014'
    assert season.first_week_date == dt.date(2014, 11, 6)
    assert season.last_week_date == dt.date(2015, 1, 8)
    assert len(season.teams) == 4

    assert Team.get_count() == 4
    assert len(Team.get_all()[0].seasons) == 1

    assert Game.get_count() == 16

