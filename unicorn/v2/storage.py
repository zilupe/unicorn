import csv
import os.path

from unicorn import unicorn_root_dir
from unicorn.configuration import logging
from unicorn.models import Season, Team, Game, Franchise

log = logging.getLogger(__name__)


class Franchises:
    def __init__(self):
        self._franchises = {f.id: f for f in Franchise.get_all()}
        self._franchise_seasons = []
        with open(os.path.join(unicorn_root_dir, 'unicorn/data/franchise_seasons.csv')) as f:
            for row in csv.DictReader(f):
                franchise_id = int(row['franchise_id'])
                if franchise_id not in self._franchises:
                    self._franchises[franchise_id] = Franchise.create(id=franchise_id)
                self._franchise_seasons.append({
                    'season_id': int(row['season_id']),
                    'gm_team_id': int(row['gm_team_id']),
                    'franchise_id': int(row['franchise_id']),
                    'team_name': row['team_name'],
                })

    def get_franchise_and_team_name(self, season_id, gm_team_id):
        for fs in self._franchise_seasons:
            if fs['season_id'] == season_id and fs['gm_team_id'] == gm_team_id:
                return self._franchises[fs['franchise_id']], fs['team_name']
        log.warning('Did not find franchise for season_id={} gm_team_id={}'.format(season_id, gm_team_id))
        return None, None


def store_season_page(page):

    # TODO This is a bit inefficient
    franchises = Franchises()

    season_obj = Season.create(
        id=page.season_id,
        name=page.season_name,
        first_week_date=page.game_days[0].date,
        last_week_date=page.game_days[-1].date,
    )

    for team in page.teams.values():
        franchise, team_name = franchises.get_franchise_and_team_name(season_obj.id, team.gm_id)

        Team.create(
            id=team.id,
            season_id=season_obj.id,
            franchise_id=franchise.id if franchise else None,
            name=team_name,
            st_position=team.position,
            st_played=team.played,
            st_won=team.won,
            st_lost=team.lost,
            st_drawn=team.drawn,
            st_forfeit_for=team.forfeit_for,
            st_forfeit_against=team.forfeit_against,
            st_score_for=team.score_for,
            st_score_against=team.score_against,
            st_score_difference=team.score_difference,
            st_bonus_points=team.bonus_points,
            st_points=team.points
        )

    for game_day in page.game_days:
        for game in game_day.games:
            Game.create(
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
