from unicorn.app import run_in_app_context
from unicorn.configuration import logging
from unicorn.models import Season, Team, Game
from unicorn.scrapers.season_pages import parse_seasons


log = logging.getLogger(__name__)


@run_in_app_context
def main():
    log.info('parsing season pages')

    all_teams = {}

    for team in Team.get_all():
        all_teams[team.id] = team

    for raw in parse_seasons():
        season = Season.create(
            id=raw['id'],
            name=raw['name'],
            first_week_date=raw['first_week_date'],
            last_week_date=raw['last_week_date'],
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
                    season=season,
                    starts_at=f_datetime,
                    home_team=home_team,
                    home_team_points=int(ht['score'] or -1),
                    away_team=away_team,
                    away_team_points=int(at['score'] or -1),
                )
            except ValueError:
                log.warning('Failed to process fixture: {}'.format(f))
                raise


if __name__ == '__main__':
    main()
