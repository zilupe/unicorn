from unicorn.app import run_in_app_context
from unicorn.configuration import logging
from unicorn.db.base import Session
from unicorn.models import Team, Game


log = logging.getLogger(__name__)

# TODO RELOADED in Summer 2015 (70) is not the today's RELOADED. It is some other team.


def remove_duplicate_teams():
    log.info('Removing duplicate teams')

    duplicate_teams = (
        # First name is of the team we want to keep
        ('Rockets', 'Euston Rockets'),
        ('Alley-Oops', 'Alley-Oops!'),
    )

    teams_to_delete = []

    for main_name, *other_names in duplicate_teams:
        main_team_id = Session.query(Team).filter(Team.name == main_name).one().id
        other_teams = Session.query(Team).filter(Team.name.in_(other_names)).all()
        other_team_ids = [t.id for t in other_teams]

        if not other_team_ids:
            continue

        for game in Session.query(Game).filter(Game.home_team_id.in_(other_team_ids)).all():
            game.home_team_id = main_team_id

        for game in Session.query(Game).filter(Game.away_team_id.in_(other_team_ids)).all():
            game.away_team_id = main_team_id

        teams_to_delete.extend(other_teams)

    Session.commit()

    for t in teams_to_delete:
        Session.delete(t)

    Session.commit()


def rename_teams():
    log.info('Renaming teams')

    renames = {
        2716: 'Supernova'
    }

    for team_id, correct_name in renames.items():
        Session.query(Team).filter(Team.id == team_id).one().name = correct_name
    Session.commit()


@run_in_app_context
def main():
    remove_duplicate_teams()
    rename_teams()


if __name__ == '__main__':
    main()
