from unicorn.models import Season, Team, Game


def test_all(db):
    Season.create(id=1)

    la = Team.create(id=1, name='Lost Angels')
    ch = Team.create(id=2, name='Camden Hells')
    ro = Team.create(id=3, name='Rockets')

    Game.create(id=1, home_team=la, away_team=ch)
    Game.create(id=2, home_team=ro, away_team=la)

    assert len(la.home_games) == 1
    assert len(la.away_games) == 1

    assert len(ch.home_games) == 0
    assert len(ch.away_games) == 1

    assert len(ro.home_games) == 1
    assert len(ro.away_games) == 0
