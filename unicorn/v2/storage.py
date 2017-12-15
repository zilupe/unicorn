from unicorn.configuration import logging
from unicorn.core.apps import current_app
from unicorn.models import Game, GameSide, Season, Team

log = logging.getLogger(__name__)


def store_season_page(page):
    season_obj = Season.create(
        id=page.season_id,
        name=page.season_name,
        first_week_date=page.game_days[0].date,
        last_week_date=page.game_days[-1].date,
        gm_league_id=page.league_id,
        gm_division_id=page.division_id,
    )

    for team in page.teams.values():
        franchise, team_name = current_app.get_franchise_and_team_name(season_obj.id, team.gm_id)

        Team.create(
            id=team.id,
            season_id=season_obj.id,
            franchise_id=franchise.id if franchise else None,
            name=team_name,
            regular_rank=team.position,
            regular_played=team.played,
            regular_won=team.won,
            regular_lost=team.lost,
            regular_drawn=team.drawn,
            regular_forfeits_for=team.forfeit_for,
            regular_forfeits_against=team.forfeit_against,
            regular_score_for=team.score_for,
            regular_score_against=team.score_against,
            regular_score_difference=team.score_difference,
            regular_bonus_points=team.bonus_points,
            regular_points=team.points,
            finals_rank=team.finals_rank,
        )

    for game_day in page.game_days:
        for game in game_day.games:
            Game.create(
                id=game.id,
                season_id=season_obj.id,
                season_stage=game.season_stage,
                starts_at=game.starts_at,
                score_status=game.score_status,
                score_status_comments=game.score_status_comments,
                sides=[
                    GameSide(
                        team_id=game.home_team_id,
                        score=game.home_team_score,
                        outcome=game.home_team_outcome,
                        points=game.home_team_points,
                    ),
                    GameSide(
                        team_id=game.away_team_id,
                        score=game.away_team_score,
                        outcome=game.away_team_outcome,
                        points=game.away_team_points,
                    ),
                ],
            )
