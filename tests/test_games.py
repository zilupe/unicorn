import datetime as dt

from unicorn.models import Franchise, Game, GameSide, Season, Team
from unicorn.values import GameOutcomes, SeasonStages


def test_winner_side_and_loser_side(db):
    f1 = Franchise.create()
    f2 = Franchise.create()
    f3 = Franchise.create()

    s1 = Season.create(first_week_date=dt.datetime(2017, 1, 1), last_week_date=dt.datetime(2017, 1, 31))
    t11 = Team.create(id='team11', season=s1, franchise=f1)
    t12 = Team.create(id='team12', season=s1, franchise=f2)
    g11 = Game.create(
        starts_at=dt.datetime(2017, 1, 1),
        season=s1,
        season_stage=SeasonStages.regular,
        sides=[
            GameSide(team=t11, score=15, outcome=GameOutcomes.lost),
            GameSide(team=t12, score=25, outcome=GameOutcomes.won),
        ]
    )
    assert g11.home_side.team is t11
    assert g11.away_side.team is t12

    assert g11.winner_side.team is t12
    assert g11.loser_side.team is t11

    g12 = Game.create(
        starts_at=dt.datetime(2017, 1, 2),
        season=s1,
        season_stage=SeasonStages.final1st,
        sides=[
            GameSide(team=t11, score=15, outcome=GameOutcomes.lost),
            GameSide(team=t12, score=18, outcome=GameOutcomes.won),
        ]
    )

    assert t11.regular_record == (0, 0, 1)
    assert t12.regular_record == (1, 0, 0)

    assert t11.finals_record == (0, 0, 1)
    assert t12.finals_record == (1, 0, 0)

    assert t11.total_record == (0, 0, 2)
    assert t12.total_record == (2, 0, 0)

    s2 = Season.create(first_week_date=dt.datetime(2017, 2, 1), last_week_date=dt.datetime(2017, 2, 28))
    t21 = Team.create(id='team21', season=s2, franchise=f1)
    t23 = Team.create(id='team23', season=s2, franchise=f3)
    g21 = Game.create(
        starts_at=dt.datetime(2017, 2, 1),
        season=s2,
        season_stage=SeasonStages.regular,
        sides=[
            GameSide(team=t23, score=19, outcome=GameOutcomes.lost),
            GameSide(team=t21, score=29, outcome=GameOutcomes.won),
        ]
    )

    assert f1.total_record == (1, 0, 2)
    assert f2.total_record == (2, 0, 0)
    assert f3.total_record == (0, 0, 1)

    assert f1.num_games == 3
    assert f1.longest_winning_streak == 1
    assert f1.longest_losing_streak == 2
    assert f1.num_20minus_conceded_games == 2
    assert f1.num_20minus_scored_games == 2
    assert f1.num_50plus_scored_games == 0
    assert f1.num_50plus_conceded_games == 0

    assert f1.largest_wins[0].plus_minus == 10
    assert f1.largest_defeats[0].plus_minus == -10
