from unicorn.models import Season, Team


def store_season_page(page):
    season_obj = Season.create(
        id=page.season_id,
        name=page.season_name,
        first_week_date=page.game_days[0].date,
        last_week_date=page.game_days[-1].date,
    )

    for team in page.teams.values():
        team_obj = Team.create(
            id=team.id
        )

        season_obj.teams.append(team_obj)
