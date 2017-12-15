from unicorn.models import Game, GameSide, Season, Team


def test_models(db):
    season = Season.create(name='Winter 2000')
    team1 = Team.create(
        id='{:0>4}.1'.format(season.id),
        season=season
    )
    team2 = Team.create(
        id='{:0>4}.2'.format(season.id),
        season=season
    )
    team3 = Team.create(
        id='{:0>4}.3'.format(season.id),
        season=season
    )

    game12 = Game.create(
        season=season,
        sides=[
            GameSide(team=team1),
            GameSide(team=team2),
        ],
    )

    game23 = Game.create(
        season=season,
        sides=[
            GameSide(team=team2),
            GameSide(team=team3),
        ],
    )

    assert len(team1.games) == 1
    assert len(team2.games) == 2
    assert len(team3.games) == 1

    assert team2.games[0].opponent.team == team1
    assert team2.games[1].opponent.team == team3
