import csv
import datetime as dt
import os

from cached_property import cached_property
from sqlalchemy import create_engine

from unicorn import unicorn_root_dir
from unicorn.runtime_context import RuntimeContext
from unicorn.core.utils import AttrDict
from unicorn.configuration import logging


log = logging.getLogger(__name__)


app_data = AttrDict({
    'franchises': None,
    'franchise_seasons': None,
    'seasons': None,
    'manual_scores': None,
    'teams': None,
})


class App(RuntimeContext):
    _allowed_vars = (
        'dry_run',
        'db_name',
    )

    @property
    def db_name(self):
        if 'db_name' in self:
            return self.get('db_name')
        else:
            return os.environ.get('UNICORN_DB_NAME', 'unicorn')

    @db_name.setter
    def db_name(self, value):
        self.set('db_name', value)

    def get_db_url(self, db_name=None):
        if db_name is None:
            db_name = self.db_name
        return (
            'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{name}'
        ).format(
            user=os.environ.get('UNICORN_DB_USER', 'root'),
            host=os.environ.get('UNICORN_DB_HOST', 'localhost'),
            password=os.environ.get('UNICORN_DB_PASSWORD', ''),
            port=os.environ.get('UNICORN_DB_PORT', 3306),
            name=db_name,
        )

    @cached_property
    def db_engine(self):
        return create_engine(self.get_db_url())

    @property
    def franchises(self):
        from unicorn.models import Franchise
        if app_data.franchises is None:
            app_data.franchises = {f.id: f for f in Franchise.get_all()}
        return app_data.franchises

    @property
    def teams(self):
        from unicorn.models import Team
        if app_data.teams is None:
            app_data.teams = {t.id: t for t in Team.get_all()}
        return app_data.teams

    @property
    def seasons(self):
        from unicorn.models import Season
        if app_data.seasons is None:
            app_data.seasons = {s.id: s for s in Season.get_all()}
        return app_data.seasons

    @cached_property
    def current_season(self):
        from unicorn.models import Season
        return sorted((s for s in Season.get_all()), key=lambda s: s.first_week_date, reverse=True)[0]

    @property
    def generation_time_str(self):
        return dt.datetime.utcnow().isoformat()

    @property
    def franchise_seasons(self):
        from unicorn.models import Franchise
        if app_data.franchise_seasons is None:
            app_data.franchise_seasons = []
            with open(os.path.join(unicorn_root_dir, 'unicorn/data/franchise_seasons.csv')) as f:
                for row in csv.DictReader(f):
                    franchise_id = int(row['franchise_id'])
                    if franchise_id not in self.franchises:
                        self.franchises[franchise_id] = Franchise.create(id=franchise_id)
                    app_data.franchise_seasons.append({
                        'season_id': int(row['season_id']),
                        'gm_team_id': int(row['gm_team_id']),
                        'franchise_id': int(row['franchise_id']),
                        'team_name': row['team_name'],
                    })
        return app_data.franchise_seasons

    @property
    def manual_scores(self):
        if app_data.manual_scores is None:
            app_data.manual_scores = {}
            with open(os.path.join(unicorn_root_dir, 'unicorn/data/manual_scores.csv')) as f:
                for row in csv.DictReader(f):
                    game_id = int(row['game_id'])
                    self.manual_scores[game_id] = {
                        'game_id': game_id,
                        'home_team_id': int(row['home_team_id'] or 0),
                        'home_team_score': int(row['home_team_score']),
                        'away_team_id': int(row['away_team_id'] or 0),
                        'away_team_score': int(row['away_team_score']),
                        'score_status': int(row['score_status']),
                        'score_status_comments': row['score_status_comments'],
                    }
        return app_data.manual_scores

    def get_franchise_and_team_name(self, season_id, gm_team_id):
        for fs in self.franchise_seasons:
            if fs['season_id'] == season_id and fs['gm_team_id'] == gm_team_id:
                return self.franchises[fs['franchise_id']], fs['team_name']
        log.warning('Did not find franchise for season_id={} gm_team_id={}'.format(season_id, gm_team_id))
        return None, None

    @cached_property
    def team_ratings(self):
        from unicorn.v2.team_ratings import TeamRatings
        team_ratings = TeamRatings()
        team_ratings.calculate()
        return team_ratings


app = App()


@app.context_entered
def context_entered(context):
    from unicorn.db.base import Session
    # TODO Ideally move Session creation to app context scope and destroy it on context exit!
    Session.configure(bind=context.db_engine)


@app.context_exited
def context_exited(context):
    pass
