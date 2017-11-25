from unicorn.models import Game, Team, Season, GameSide
from unicorn.values import GameOutcomes


def test_winner_side_and_loser_side(db):
    season = Season.create()
    team1 = Team.create(id='team1', season=season)
    team2 = Team.create(id='team2', season=season)
    g1 = Game.create(
        season=season,
        sides=[
            GameSide(team=team1, score=15, outcome=GameOutcomes.lost),
            GameSide(team=team2, score=25, outcome=GameOutcomes.won),
        ]
    )
    assert g1.home_side.team is team1
    assert g1.away_side.team is team2

    assert g1.winner_side.team is team2
    assert g1.loser_side.team is team1
