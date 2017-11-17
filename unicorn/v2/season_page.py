import datetime as dt
from urllib.parse import parse_qs

from bs4 import BeautifulSoup

from unicorn.values import SeasonStages


def parse_gm_date(date_str):
    """
    Parses date in the format "Thursday 06 Nov 2014"
    and returns a datetime.
    """
    return dt.datetime.strptime(date_str, '%A %d %b %Y')


def parse_gm_time(time_str):
    return dt.datetime.strptime(time_str, '%H:%M')


def extract_from_link(link, field):
    return parse_qs(link['href'])[field][0]


class AttrDict(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, super().__repr__())


class Game(AttrDict):
    pass


class GameDay(AttrDict):
    pass


class Team(AttrDict):
    pass


class SeasonPage:
    @classmethod
    def from_html_file(cls, filename):
        with open(filename) as f:
            return cls.from_input_str(f.read())

    @classmethod
    def from_input_str(cls, input_str):
        page = cls()
        page.parse(input_str)
        return page

    def __init__(self):
        self.soup = None
        self.game_days = None
        self.season_id = None
        self.season_name = None
        self.teams = None

        # Not important for us at the moment
        self.league_id = None
        self.division_id = None

    def parse(self, input_str):
        self.soup = BeautifulSoup(input_str, 'html.parser')

        self.season_name = self.soup.find('head').find('title').text.strip().split(' - ')[4]

        self.game_days = []
        self.teams = {}

        season_stage = SeasonStages.regular

        for week_number, t in enumerate(self.soup.find_all('table', class_='FTable')):
            week_date = parse_gm_date(t.find('tr', class_='FHeader').find('td').text.strip())
            week_games = []
            for g in t.find_all('tr', class_='FRow'):
                sc = g.find('td', class_='FTitle')
                if sc:
                    decoded_ss = SeasonStages.decode_gm_season_stage(sc.text.strip())
                    if decoded_ss is not None:
                        season_stage = decoded_ss

                tc = g.find('td', class_='FDate')
                if not tc:
                    continue
                game_time = parse_gm_time(tc.text.strip())

                ic = g.find('td', class_='FScore')
                if not ic:
                    continue
                game_id = int(ic.find('nobr')['data-fixture-id'])
                game_score = ic.find('nobr').find('div').find('nobr').text.strip().split(' - ')

                game_venue = g.find('td', class_='FPlayingArea').text.strip()

                htc = g.find('td', class_='FHomeTeam')
                atc = g.find('td', class_='FAwayTeam')

                if self.season_id is None:
                    self.season_id = int(extract_from_link(htc.find('a'), 'SeasonId'))
                    self.league_id = int(extract_from_link(htc.find('a'), 'LeagueId'))
                    self.division_id = int(extract_from_link(htc.find('a'), 'DivisionId'))

                game = Game(
                    id=game_id,
                    starts_at=game_time.replace(
                        year=week_date.year, month=week_date.month, day=week_date.day
                    ),
                    season_stage=season_stage,
                    venue=game_venue,
                    home_team_id=int(extract_from_link(htc.find('a'), 'TeamId')),
                    home_team_points=int(game_score[0]),
                    away_team_id=int(extract_from_link(atc.find('a'), 'TeamId')),
                    away_team_points=int(game_score[1]),
                )
                week_games.append(game)

                if game.home_team_id not in self.teams:
                    self.teams[game.home_team_id] = Team(id=game.home_team_id)

                if game.away_team_id not in self.teams:
                    self.teams[game.away_team_id] = Team(id=game.away_team_id)

            self.game_days.append(GameDay(
                date=week_date,
                week_number=week_number,
                games=week_games,
            ))
