import re

import collections

import itertools
from cached_property import cached_property
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from unicorn.configuration import logging
from unicorn.core.apps import current_app
from unicorn.db.base import Base
from unicorn.values import SeasonStages, GameOutcomes


log = logging.getLogger(__name__)


def compile_game_sides_record(game_sides):
    return (
        sum(1 for gs in game_sides if gs.is_won),
        sum(1 for gs in game_sides if gs.is_drawn),
        sum(1 for gs in game_sides if gs.is_lost),
    )


def compile_points_difference_avg(game_sides):
    return (
        (sum(gs.score for gs in game_sides) - sum(gs.opponent.score for gs in game_sides))
        /
        len(game_sides)
    )


class Franchise(Base):
    __tablename__ = 'franchises'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(String(20))

    colors = Column(String(255))

    teams = relationship('Team', back_populates='franchise')

    @cached_property
    def num_seasons(self):
        return len(self.teams)

    @cached_property
    def num_games(self):
        return sum(len(t.games) for t in self.teams)

    @cached_property
    def regular_record(self):
        return (
            sum(t.regular_record[0] for t in self.teams),
            sum(t.regular_record[1] for t in self.teams),
            sum(t.regular_record[2] for t in self.teams),
        )

    @cached_property
    def finals_record(self):
        return (
            sum(t.finals_record[0] for t in self.teams),
            sum(t.finals_record[1] for t in self.teams),
            sum(t.finals_record[2] for t in self.teams),
        )

    @cached_property
    def total_record(self):
        return (
            self.regular_record[0] + self.finals_record[0],
            self.regular_record[1] + self.finals_record[1],
            self.regular_record[2] + self.finals_record[2],
        )

    @property
    def games(self):
        for t in self.teams:
            yield from t.games

    @property
    def games_reversed(self):
        yield from sorted(self.games, key=lambda gs: gs.game.starts_at, reverse=True)

    @cached_property
    def last05_games(self):
        games = list(itertools.islice(self.games_reversed, 5))
        return games

    @cached_property
    def last05_record(self):
        return compile_game_sides_record(self.last05_games)

    @cached_property
    def last05_points_difference_avg(self):
        return compile_points_difference_avg(self.last05_games)

    @cached_property
    def last15_games(self):
        games = list(itertools.islice(self.games_reversed, 15))
        return games

    @cached_property
    def last15_record(self):
        return compile_game_sides_record(self.last15_games)

    @cached_property
    def last15_points_difference_avg(self):
        return compile_points_difference_avg(self.last15_games)

    @cached_property
    def year2017_games(self):
        return [gs for gs in self.games_reversed if gs.game.starts_at.year == 2017]

    @cached_property
    def year2017_record(self):
        return compile_game_sides_record(self.year2017_games)

    @cached_property
    def year2017_points_difference_avg(self):
        return compile_points_difference_avg(self.year2017_games)

    @cached_property
    def finals_winners_teams(self):
        return [t for t in self.teams if t.season.finals_finished and t.finals_rank == 1]

    @cached_property
    def num_finals_winners_teams(self):
        return len(self.finals_winners_teams)

    @cached_property
    def regular_winners_teams(self):
        return [t for t in self.teams if t.season.regular_finished and t.regular_rank == 1]

    @cached_property
    def num_regular_winners_teams(self):
        return len(self.regular_winners_teams)

    @cached_property
    def teams_sorted(self):
        return sorted(self.teams, key=lambda t: t.season.first_week_date)

    @cached_property
    def teams_by_all_seasons(self):
        teams = collections.OrderedDict()

        for season in current_app.seasons.values():
            teams[season] = None

        for team in self.teams:
            teams[team.season] = team

        return teams

    @cached_property
    def color1(self):
        if self.colors:
            return self.colors.split(',')[0]
        else:
            return '#CCCCCC'

    @cached_property
    def color2(self):
        if self.colors:
            return self.colors.split(',')[-1]
        else:
            return '#EEEEEE'

    @cached_property
    def logo_html(self):
        return (
            '<div class="franchise-logo-left franchise-{0}"></div>'
            '<div class="franchise-logo-right franchise-{0}"></div>'
        ).format(self.id)

    @cached_property
    def trophy_list_html(self):
        return '<sup>{}</sup>'.format(
            ' '.join(
                '<span class="icon trophy">7</span>'
                for x in range(self.num_finals_winners_teams)
            )
        )

    @cached_property
    def h2h_stats(self):
        from unicorn.stats import FranchiseHead2HeadStats

        stats = []
        for franchise in Franchise.get_all():
            if franchise is self:
                continue
            stats.append(FranchiseHead2HeadStats(us=self, them=franchise))
        return stats

    @property
    def sparkline_labels(self):
        return ', '.join(str(s.number) for s in self.teams_by_all_seasons.keys())

    @property
    def sparkline_data(self):
        ceiling = 10
        data = []
        for s, t in self.teams_by_all_seasons.items():
            if t is None:
                data.append(0)
            elif t.finals_rank:
                data.append(ceiling - t.finals_rank + 1)
            else:
                log.warning('Team {} is missing finals_rank in season {}'.format(t, s))
                data.append(0)
        return ', '.join(str(d) for d in data)

    @property
    def game_achievements(self):
        achievements = {
            'longest_winning_streak': 0,
            'longest_losing_streak': 0,
            'num_50plus_scored_games': 0,
            'num_50plus_conceded_games': 0,
            'num_20minus_scored_games': 0,
            'num_20minus_conceded_games': 0,
            'largest_wins': [],
            'largest_defeats': [],
            'best_offensive_games': [],
            'worst_offensive_games': [],
            'best_defensive_games': [],
            'worst_defensive_games': [],
        }
        longest_winning_streak = []
        longest_losing_streak = []
        current_streak = []

        def complete_current_streak():
            if not current_streak:
                return

            if current_streak[-1].is_won:
                if len(current_streak) > len(longest_winning_streak):
                    longest_winning_streak[:] = list(current_streak)
            else:
                if len(current_streak) > len(longest_losing_streak):
                    longest_losing_streak[:] = list(current_streak)
            achievements['longest_winning_streak'] = len(longest_winning_streak)
            achievements['longest_losing_streak'] = len(longest_losing_streak)
            current_streak[:] = []

        for gs in self.games:
            # Offensive and Defensive achievements

            if gs.score >= 50:
                achievements['num_50plus_scored_games'] += 1
            elif gs.score <= 20 and gs.outcome not in (GameOutcomes.forfeit_against, GameOutcomes.forfeit_for):
                achievements['num_20minus_scored_games'] += 1

            if gs.opponent.score >= 50:
                achievements['num_50plus_conceded_games'] += 1
            elif gs.opponent.score <= 20 and gs.outcome not in (GameOutcomes.forfeit_against, GameOutcomes.forfeit_for):
                achievements['num_20minus_conceded_games'] += 1

            # Streaks

            if not current_streak:
                if gs.is_won or gs.is_lost:
                    current_streak.append(gs)
                else:
                    # Ignore draws
                    pass
            else:
                if (gs.is_won and current_streak[-1].is_won) or (gs.is_lost and current_streak[-1].is_lost):
                    current_streak.append(gs)
                else:
                    complete_current_streak()
                    current_streak.append(gs)

        complete_current_streak()

        by_points_difference = sorted(
            (gs for gs in self.games if gs.was_played),
            key=lambda gs: gs.plus_minus
        )
        n = min(5, len(by_points_difference))
        achievements['largest_wins'] = list(gs for gs in reversed(by_points_difference[-n:]) if gs.is_won)
        achievements['largest_defeats'] = list(gs for gs in by_points_difference[:n] if gs.is_lost)

        by_points_scored = sorted(
            (gs for gs in self.games if gs.was_played),
            key=lambda gs: gs.score,
        )
        n = min(5, len(by_points_scored))
        achievements['best_offensive_games'] = list(reversed(by_points_scored[-n:]))
        achievements['worst_offensive_games'] = by_points_scored[:n]

        by_points_conceded = sorted(
            (gs for gs in self.games if gs.was_played),
            key=lambda gs: gs.opponent.score,
        )
        achievements['best_defensive_games'] = by_points_conceded[:n]
        achievements['worst_defensive_games'] = list(reversed(by_points_conceded[-n:]))

        return achievements

    def __getattr__(self, item):
        if not item.startswith('_'):
            return self.game_achievements[item]
        else:
            return super().__getattribute__(item)


Franchise.default_order_by = [Franchise.name.asc(),]


class Team(Base):
    """
    Team represents a collective of players playing under one name for for one specific season.

    Team is identified by GoMammoth's <SeasonId>.<TeamId>
    because GoMammoth reuse TeamIds for somewhat unrelated teams across seasons
    and sometimes a franchise has used more than one GoMammoth's TeamId.
    """
    __tablename__ = 'teams'

    id = Column(String(15), primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season', back_populates='teams')
    franchise_id = Column(Integer, ForeignKey('franchises.id'))
    franchise = relationship('Franchise', back_populates='teams')
    name = Column(String(50))

    # Standings table columns
    regular_rank = Column(Integer)
    regular_played = Column(Integer)
    regular_won = Column(Integer)
    regular_lost = Column(Integer)
    regular_drawn = Column(Integer)
    regular_forfeits_for = Column(Integer)
    regular_forfeits_against = Column(Integer)
    regular_score_for = Column(Integer)
    regular_score_against = Column(Integer)
    regular_score_difference = Column(Integer)
    regular_bonus_points = Column(Integer)
    regular_points = Column(Integer)

    # Finals aggregates
    finals_rank = Column(Integer)

    games = relationship('GameSide')

    @cached_property
    def regular_games(self):
        return [gs for gs in self.games if gs.game.is_regular]

    @cached_property
    def finals_games(self):
        return [gs for gs in self.games if not gs.game.is_regular]

    def __getattr__(self, item):
        parts = item.split('_')

        if len(parts) < 2:
            raise AttributeError(item)

        prefix = parts[0]
        suffix = parts[-1]

        if prefix not in ('regular', 'finals', 'total'):
            raise AttributeError(item)

        without_prefix = '_'.join(parts[1:])

        if prefix in ('regular', 'finals'):
            games = getattr(self, '{}_games'.format(prefix))
        else:
            games = self.games

        num_games_decided = sum(1 for gs in games if gs.is_decided)

        if without_prefix == 'num_games_decided':
            return num_games_decided

        elif without_prefix == 'win_percentage':
            if num_games_decided == 0:
                return 0
            return 100.0 * sum(1 for gs in games if gs.is_won) / num_games_decided

        elif suffix == 'avg':
            # Automatic finals|regular_<stat>_avg calculation

            if num_games_decided == 0:
                return 0

            metric = without_prefix.rsplit('_', 1)[0]
            if hasattr(self, metric):
                # Metric available on Team
                total = getattr(self, metric)
            elif hasattr(GameSide, metric):
                # Metric available on GameSide, must sum up
                total = sum(getattr(gs, metric) for gs in games if gs.is_decided)
            elif metric == 'score_for':
                # Custom metric
                total = sum(gs.score for gs in games if gs.is_decided)
            elif metric == 'score_against':
                # Custom metric
                total = sum(gs.opponent.score for gs in games if gs.is_decided)
            elif metric == 'score_difference':
                # Custom metric
                total = sum(gs.score - gs.opponent.score for gs in games if gs.is_decided)
            else:
                raise AttributeError(item)

            return total / num_games_decided

        elif hasattr(GameSide, without_prefix):
            # Must aggregate all games
            return sum(getattr(gs, without_prefix) for gs in games)

        else:
            raise AttributeError(item)

    @cached_property
    def regular_record(self):
        return compile_game_sides_record(self.regular_games)

    @cached_property
    def regular_record_str(self):
        return '-'.join(str(r) for r in self.regular_record)

    @cached_property
    def finals_record(self):
        return compile_game_sides_record(self.finals_games)

    @cached_property
    def finals_record_str(self):
        return '-'.join(str(r) for r in self.finals_record)

    @cached_property
    def total_record(self):
        regular = self.regular_record
        finals = self.finals_record
        return (
            regular[0] + finals[0],
            regular[1] + finals[1],
            regular[2] + finals[2],
        )

    @cached_property
    def total_record_str(self):
        return '-'.join(str(r) for r in self.total_record)


Team.default_order_by = [Team.name.asc(),]


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)

    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season', back_populates='games')

    season_stage = Column(String(20), server_default=SeasonStages.regular)
    starts_at = Column(DateTime)

    score_status = Column(Integer, default=0)
    score_status_comments = Column(String(255))

    notes = Column(Text)

    sides = relationship('GameSide', back_populates='game')

    @property
    def simple_label(self):
        return self.id

    @property
    def is_regular(self):
        return self.season_stage == SeasonStages.regular

    @property
    def home_side(self):
        return self.sides[0]

    @property
    def away_side(self):
        return self.sides[1]

    @cached_property
    def date_str(self):
        return self.starts_at.strftime('%Y-%m-%d')

    @cached_property
    def pretty_date_str(self):
        return self.starts_at.strftime('%d %b %Y')

    @cached_property
    def time_str(self):
        return self.starts_at.strftime('%H:%M')

    @cached_property
    def score_link(self):
        return '<a href="{}">{} - {}{}</a>'.format(
            self.simple_url,
            self.home_side.score,
            self.away_side.score,
            '<sup>MS</sup>' if self.score_status > 1 else '',
        )

    @cached_property
    def winner_side(self):
        return sorted(self.sides, key=lambda gs: (0 - gs.score, gs.team.name, gs.team.id))[0]

    @cached_property
    def loser_side(self):
        return sorted(self.sides, key=lambda gs: (0 - gs.score, gs.team.name, gs.team.id))[-1]

    @property
    def plus_minus(self):
        return self.winner_side.score - self.loser_side.score


Game.default_order_by = [Game.starts_at.asc(),]


class GameSide(Base):
    __tablename__ = 'game_sides'

    id = Column(Integer, primary_key=True)

    team_id = Column(String(15), ForeignKey('teams.id'), nullable=False)
    team = relationship('Team', foreign_keys=team_id)

    score = Column(Integer)
    points = Column(Integer)
    outcome = Column(String(5))

    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship('Game', back_populates='sides')

    @property
    def is_decided(self):
        return self.score is not None and self.outcome in GameOutcomes.decided

    @property
    def was_played(self):
        return (
            self.score is not None
            and
            self.outcome not in (GameOutcomes.missing, GameOutcomes.forfeit_for, GameOutcomes.forfeit_against)
        )

    @property
    def is_won(self):
        return self.is_decided and self.outcome in (GameOutcomes.won, GameOutcomes.forfeit_for)

    @property
    def is_drawn(self):
        return self.is_decided and self.outcome in (GameOutcomes.drawn,)

    @property
    def is_lost(self):
        return self.is_decided and self.outcome in (GameOutcomes.lost, GameOutcomes.forfeit_against)

    @cached_property
    def opponent(self):
        for side in self.game.sides:
            if side != self:
                return side

    @cached_property
    def score_link(self):
        """
        This is different from Game.score_link because this always prints the current side first!
        """
        return '<a href="{}">{} - {}{}</a>'.format(
            self.game.simple_url,
            self.score,
            self.opponent.score,
            '<sup>MS</sup>' if self.game.score_status > 1 else '',
        )

    @cached_property
    def date_link(self):
        return '<a href="{}">{}</a>'.format(
            self.game.simple_url,
            self.game.date_str,
        )

    @property
    def plus_minus(self):
        if self.score is not None:
            return self.score - self.opponent.score
        else:
            return None


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    number = Column(String(2), nullable=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    teams = relationship('Team', back_populates='season')

    @property
    def simple_label(self):
        return '{} - {}'.format(self.number, self.name).replace(' ', '&nbsp;')

    @cached_property
    def short_name(self):
        return re.sub('[^a-zA-Z0-9]', '', self.name)

    @cached_property
    def num_teams(self):
        return len(self.teams)

    @cached_property
    def first_week_date_str(self):
        return self.first_week_date.strftime('%Y-%m-%d')

    @cached_property
    def last_week_date_str(self):
        return self.last_week_date.strftime('%Y-%m-%d')

    @property
    def date_range_str(self):
        return '{} - {}'.format(self.first_week_date_str, self.last_week_date_str)

    @cached_property
    def regular_finished(self):
        # TODO Implement this
        return True

    @cached_property
    def regular_teams_ranked(self):
        """
        Teams in the order they are ranked in the regular season.
        """
        return sorted(self.teams, key=lambda t: t.regular_rank or 100)

    @cached_property
    def regular_champions(self):
        return self.regular_teams_ranked[0]

    @cached_property
    def finals_finished(self):
        return self.finals_champions.finals_rank == 1

    @cached_property
    def finals_teams_ranked(self):
        """
        Teams in the order they are ranked after the finals.
        """
        return sorted(self.teams, key=lambda t: t.finals_rank or 100)

    @cached_property
    def finals_champions(self):
        return self.finals_teams_ranked[0]

    @cached_property
    def date_range_link(self):
        return '<a href="{}">{}</a>'.format(self.simple_url, self.date_range_str)


Season.default_order_by = [Season.first_week_date.asc(),]


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')

