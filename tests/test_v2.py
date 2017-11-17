import datetime as dt
import os.path

from unicorn import unicorn_root_dir
from unicorn.models import Season, Team, Game
from unicorn.v2 import process_season_page
from unicorn.values import SeasonStages


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

    all_games = list(Game.get_all())
    assert len(all_games) == 16

    first_game = all_games[0]
    assert first_game.id == 50627
    assert first_game.home_team_id == 3770
    assert first_game.away_team_id == 2716
    assert first_game.season_stage == SeasonStages.regular
    assert first_game.home_team_points == 41
    assert first_game.away_team_points == 52
    assert first_game.season_id == season.id
    assert first_game.starts_at == dt.datetime(2014, 11, 6, 19, 0)

    # for g in all_games:
    #     print(g.id, g.starts_at, g.home_team_points, g.away_team_points)

    assert all_games[-4].season_stage == SeasonStages.semifinal1
    assert all_games[-3].season_stage == SeasonStages.semifinal2
    assert all_games[-2].season_stage == SeasonStages.final1st
    assert all_games[-1].season_stage == SeasonStages.final3rd
