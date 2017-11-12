from unicorn.configuration import get_session, db_engine, logging
from unicorn.models import Season, Base, Team, Game
from unicorn.season_pages import parse_seasons


log = logging.getLogger(__name__)


def list_models(model_cls):
    print('{}:'.format(model_cls.__name__))
    for obj in get_session().query(model_cls).all():
        print(obj)
    print('---')


def main():
    Base.metadata.create_all(db_engine)

    all_teams = {}

    for team in Team.get_all():
        all_teams[team.id] = team

    for i, raw in enumerate(parse_seasons()):
        season_id = i + 1
        season = Season.create(
            id=season_id,
            name=raw['name'],
        )

        for t in raw['teams']:
            if t['id'] not in all_teams:
                all_teams[t['id']] = Team.create(
                    id=t['id'],
                    name=t['name'],
                )

        for f in raw['fixtures']:
            f_datetime, ht, at = f
            try:
                home_team = all_teams[ht['id']]
                away_team = all_teams[at['id']]
                Game.create(
                    starts_at=f_datetime,
                    home_team=home_team,
                    home_team_points=int(ht['score'] or -1),
                    away_team=away_team,
                    away_team_points=int(at['score'] or -1),
                )
            except ValueError:
                log.warning('Failed to process fixture: {}'.format(f))
                raise


    list_models(Team)
    list_models(Season)
    list_models(Game)


if __name__ == '__main__':
    main()

