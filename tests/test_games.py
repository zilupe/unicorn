from unicorn.models import Game, Team, Season, GameSide, Franchise
from unicorn.values import GameOutcomes, SeasonStages


def test_winner_side_and_loser_side(db):
    f1 = Franchise.create()
    f2 = Franchise.create()
    f3 = Franchise.create()

    s1 = Season.create()
    t11 = Team.create(id='team11', season=s1, franchise=f1)
    t12 = Team.create(id='team12', season=s1, franchise=f2)
    g11 = Game.create(
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

    s2 = Season.create()
    t21 = Team.create(id='team21', season=s2, franchise=f1)
    t23 = Team.create(id='team23', season=s2, franchise=f3)
    g21 = Game.create(
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
