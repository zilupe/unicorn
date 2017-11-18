from unicorn.models import Season, Team, TeamSeason, Game


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

        team_season_obj = TeamSeason.create(
            team_id=team_obj.id,
            season_id=season_obj.id,
            team_name=None,
        )

    for game_day in page.game_days:
        for game in game_day.games:
            game_obj = Game.create(
                id=game.id,
                season_id=season_obj.id,
                season_stage=game.season_stage,
                starts_at=game.starts_at,
                home_team_id=game.home_team_id,
                home_team_score=game.home_team_score,
                home_team_points=game.home_team_points,
                home_team_outcome=game.home_team_outcome,
                away_team_id=game.away_team_id,
                away_team_points=game.away_team_points,
                away_team_score=game.away_team_score,
                away_team_outcome=game.away_team_outcome,
            )
