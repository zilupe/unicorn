from unicorn.app import run_in_app_context
from unicorn.db.base import Session
from unicorn.models import Team, Game


def apply_team_corrections():
    combine_teams_by_name = (
        ('Rockets', 'Euston Rockets'),
        ('Alley-Oops', 'Alley-Oops!'),
    )

    teams_to_delete = []

    for main_name, *other_names in combine_teams_by_name:
        main_team_id = Session.query(Team).filter(Team.name==main_name).one().id
        other_teams = Session.query(Team).filter(Team.name.in_(other_names)).all()
        other_team_ids = [t.id for t in other_teams]

        if not other_team_ids:
            continue

        for game in Session.query(Game).filter(Game.home_team_id.in_(other_team_ids)).all():
            game.home_team_id = main_team_id
            Session.commit()

        for game in Session.query(Game).filter(Game.away_team_id.in_(other_team_ids)).all():
            game.away_team_id = main_team_id
            Session.commit()

        teams_to_delete.extend(other_teams)

    for t in teams_to_delete:
        Session.delete(t)

    Session.commit()


@run_in_app_context
def main():
    apply_team_corrections()


if __name__ == '__main__':
    main()
