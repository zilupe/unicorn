import datetime as dt
import os.path

from unicorn import unicorn_root_dir
from unicorn.models import Season, Game
from unicorn.v2 import process_season_page
from unicorn.values import SeasonStages, GameOutcomes


def test_processes_autumn_2014_season_page(db):
    input_file = os.path.join(unicorn_root_dir, 'input/season-pages/2014-Autumn.htm')
    assert os.path.isfile(input_file)

    process_season_page(input_file)

    season = Season.get_by_id(55)
    assert season.id == 55
    assert season.name == 'Autumn 2014'
    assert season.first_week_date == dt.date(2014, 11, 6)
    assert season.last_week_date == dt.date(2015, 1, 8)
    assert len(season.teams) == 4

    all_games = list(Game.get_all().filter(Game.season_id == season.id))
    assert len(all_games) == 16

    first_game = all_games[0]
    assert first_game.id == 50627
    assert first_game.home_team_id == 3770
    assert first_game.home_team_score == 41
    assert first_game.home_team_outcome == GameOutcomes.lost
    assert first_game.home_team_points == 1
    assert first_game.away_team_id == 2716
    assert first_game.away_team_score == 52
    assert first_game.away_team_outcome == GameOutcomes.won
    assert first_game.away_team_points == 3
    assert first_game.season_stage == SeasonStages.regular
    assert first_game.season_id == season.id
    assert first_game.starts_at == dt.datetime(2014, 11, 6, 19, 0)

    # Thursday 13 Nov 2014
    # Camden Hells 20 - 0 Upper Street Ballers
    assert all_games[2].season_stage == SeasonStages.regular
    assert all_games[2].home_team_score == 20
    assert all_games[2].home_team_outcome == GameOutcomes.forfeit_for
    assert all_games[2].home_team_points == 3
    assert all_games[2].away_team_score == 0
    assert all_games[2].away_team_outcome == GameOutcomes.forfeit_against
    assert all_games[2].away_team_points == 1

    # Thursday 18 Dec 2014 Semi Final 1
    # LKA Clippers 20 - 0 Pentonville Pacers
    assert all_games[-4].season_stage == SeasonStages.semifinal1
    assert all_games[-4].home_team_score == 20
    assert all_games[-4].home_team_outcome == GameOutcomes.forfeit_for
    assert all_games[-4].home_team_points == 0  # No points for playoff games
    assert all_games[-4].away_team_score == 0
    assert all_games[-4].away_team_outcome == GameOutcomes.forfeit_against
    assert all_games[-4].away_team_points == 0

    assert all_games[-3].season_stage == SeasonStages.semifinal2
    assert all_games[-2].season_stage == SeasonStages.final1st
    assert all_games[-1].season_stage == SeasonStages.final3rd

    # Supernova aka LKA Clippers TeamSeason
    ts = all_games[-2].home_team.seasons[0]
    assert ts.st_position == 1
    assert ts.st_played == 6
    assert ts.st_won == 5
    assert ts.st_lost == 1
    assert ts.st_drawn == 0
    # Looks like GoMammoth don't actually register forfeits properly.
    assert ts.st_forfeit_for == 0
    assert ts.st_forfeit_against == 0
    assert ts.st_score_for == 279
    assert ts.st_score_against == 229
    assert ts.st_score_difference == 50
    assert ts.st_bonus_points == 0
    assert ts.st_points == 16