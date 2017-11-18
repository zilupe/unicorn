import csv
import functools
import os.path

from unicorn import unicorn_root_dir
from unicorn.configuration import logging
from unicorn.core.apps import App
from unicorn.models import Franchise
from unicorn.v2.season_page import AttrDict

log = logging.getLogger(__name__)


app_data = AttrDict({
    'franchises': None,
    'franchise_seasons': None,
})


class UnicornApp(App):
    @property
    def franchises(self):
        if app_data.franchises is None:
            app_data.franchises = {f.id: f for f in Franchise.get_all()}
        return app_data.franchises

    @property
    def franchise_seasons(self):
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

    def get_franchise_and_team_name(self, season_id, gm_team_id):
        for fs in self.franchise_seasons:
            if fs['season_id'] == season_id and fs['gm_team_id'] == gm_team_id:
                return self.franchises[fs['franchise_id']], fs['team_name']
        log.warning('Did not find franchise for season_id={} gm_team_id={}'.format(season_id, gm_team_id))
        return None, None


def create_app(**kwargs):
    app = UnicornApp(**kwargs)

    # TODO Make this cleaner later
    import unicorn.db.connection

    return app


def run_in_app_context(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        with create_app():
            f()

    return wrapped
