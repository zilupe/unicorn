import datetime as dt
from urllib.parse import parse_qs

from bs4 import BeautifulSoup

from unicorn.configuration import logging
from unicorn.core.apps import current_app
from unicorn.values import SeasonStages, GameOutcomes, ScoreStatuses

log = logging.getLogger(__name__)


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

    def unicorn_team_id(self, gm_team_id):
        """
        Build unicorn team id which consists of GM SeasonId concatenated with GM TeamId
        """
        return '{:0>4}.{}'.format(int(self.season_id), int(gm_team_id))

    def parse(self, input_str):
        # Do not extract team names because we are assigning them manually --
        # GoMammoth shows the latest team name in all seasons.

        self.soup = BeautifulSoup(input_str, 'html.parser')

        self.season_name = self.soup.find('head').find('title').text.strip().split(' - ')[4]

        if self.season_id is None:
            self.season_id = int(extract_from_link(self.soup.find('h3').find('a'), 'SeasonId'))

        self.teams = {}
        for i, st_tr in enumerate(self.soup.find('table', class_='STTable').find_all('tr', class_='STRow')):
            gm_team_id = int(extract_from_link(st_tr.find('td', class_='STTeamCell').find('a'), 'TeamId'))
            team_id = self.unicorn_team_id(gm_team_id)
            tds = st_tr.find_all('td')
            self.teams[team_id] = Team(
                id=team_id,
                gm_id=gm_team_id,
                position=i + 1,
                played=int(tds[2].text.strip()),
                won=int(tds[3].text.strip()),
                lost=int(tds[4].text.strip()),
                drawn=int(tds[5].text.strip()),
                forfeit_for=int(tds[6].text.strip()),
                forfeit_against=int(tds[7].text.strip()),
                score_for=int(tds[8].text.strip()),
                score_against=int(tds[9].text.strip()),
                score_difference=int(tds[10].text.strip()),
                bonus_points=int(tds[11].text.strip()),
                points=int(tds[12].find('a').text.strip()),

                finals_rank=None,
            )

        self.game_days = []
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
                game_time_str = tc.text.strip()
                if game_time_str == 'Bye':
                    continue
                game_time = parse_gm_time(game_time_str)

                ic = g.find('td', class_='FScore')
                if not ic:
                    continue
                game_id = int(ic.find('nobr')['data-fixture-id'])

                game_score_status = ScoreStatuses.winner_and_score_ok
                game_score_status_comments = None
                game_home_team_id = None
                game_away_team_id = None

                if game_id in current_app.manual_scores:
                    fs = current_app.manual_scores[game_id]
                    game_home_team_id = fs['home_team_id']
                    game_away_team_id = fs['away_team_id']
                    game_score = (fs['home_team_score'], fs['away_team_score'])
                    game_score_status = fs['score_status']
                    game_score_status_comments = fs['score_status_comments']
                else:
                    if ic.find('nobr').find('div'):
                        game_score = (
                            ic.find('nobr').find('div').find('nobr').text.strip().split(' - ')
                        )
                    else:
                        log.warning((
                            'Encountered a game with no score and no manual score provided: '
                            'week_date={} game_time={} game_id={}'
                        ).format(week_date, game_time, game_id))
                        game_score = (None, None)
                        game_score_status = ScoreStatuses.unknown
                        game_score_status_comments = 'Unresolved'

                game_venue = g.find('td', class_='FPlayingArea').text.strip()

                htc = g.find('td', class_='FHomeTeam')
                atc = g.find('td', class_='FAwayTeam')

                game = Game(
                    id=game_id,
                    starts_at=game_time.replace(
                        year=week_date.year, month=week_date.month, day=week_date.day
                    ),
                    season_stage=season_stage,
                    venue=game_venue,
                    home_team_id=self.unicorn_team_id(game_home_team_id or extract_from_link(htc.find('a'), 'TeamId')),
                    home_team_score=int(game_score[0]) if game_score[0] is not None else None,
                    away_team_id=self.unicorn_team_id(game_away_team_id or extract_from_link(atc.find('a'), 'TeamId')),
                    away_team_score=int(game_score[1]) if game_score[1] is not None else None,
                    score_status=game_score_status,
                    score_status_comments=game_score_status_comments,
                )

                game.home_team_outcome, game.away_team_outcome = GameOutcomes.from_scores(
                    game.home_team_score,
                    game.away_team_score,
                )
                game.home_team_points = GameOutcomes.get_points_for(game.home_team_outcome, season_stage)
                game.away_team_points = GameOutcomes.get_points_for(game.away_team_outcome, season_stage)

                week_games.append(game)

                if season_stage == SeasonStages.final1st:
                    if game.home_team_outcome in (GameOutcomes.won, GameOutcomes.forfeit_for):
                        self.teams[game.home_team_id].finals_rank = 1
                        self.teams[game.away_team_id].finals_rank = 2
                    elif game.home_team_outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against):
                        self.teams[game.home_team_id].finals_rank = 2
                        self.teams[game.away_team_id].finals_rank = 1
                elif season_stage == SeasonStages.final3rd:
                    if game.home_team_outcome in (GameOutcomes.won, GameOutcomes.forfeit_for):
                        self.teams[game.home_team_id].finals_rank = 3
                        self.teams[game.away_team_id].finals_rank = 4
                    elif game.home_team_outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against):
                        self.teams[game.home_team_id].finals_rank = 4
                        self.teams[game.away_team_id].finals_rank = 3
                elif season_stage == SeasonStages.final5th:
                    if game.home_team_outcome in (GameOutcomes.won, GameOutcomes.forfeit_for):
                        self.teams[game.home_team_id].finals_rank = 5
                        self.teams[game.away_team_id].finals_rank = 6
                    elif game.home_team_outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against):
                        self.teams[game.home_team_id].finals_rank = 6
                        self.teams[game.away_team_id].finals_rank = 5
                elif season_stage == SeasonStages.final7th:
                    if game.home_team_outcome in (GameOutcomes.won, GameOutcomes.forfeit_for):
                        self.teams[game.home_team_id].finals_rank = 7
                        self.teams[game.away_team_id].finals_rank = 8
                    elif game.home_team_outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against):
                        self.teams[game.home_team_id].finals_rank = 8
                        self.teams[game.away_team_id].finals_rank = 7
                elif season_stage == SeasonStages.semifinal5th1:
                    # In a 7 team league losing 5th place semifinal means you finish last (7th)
                    if game.home_team_outcome in (GameOutcomes.won, GameOutcomes.forfeit_for):
                        self.teams[game.away_team_id].finals_rank = 7
                    elif game.home_team_outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against):
                        self.teams[game.home_team_id].finals_rank = 7

            self.game_days.append(GameDay(
                date=week_date,
                week_number=week_number,
                games=week_games,
            ))
