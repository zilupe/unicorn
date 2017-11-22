import re

import collections
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from unicorn.core.apps import current_app
from unicorn.core.utils import cached_property
from unicorn.db.base import Base
from unicorn.values import SeasonStages, GameOutcomes


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
    def finals_num_winners(self):
        return sum(1 for t in self.teams if t.season.finals_finished and t.finals_rank == 1)

    @cached_property
    def regular_num_winners(self):
        return sum(1 for t in self.teams if t.season.regular_finished and t.regular_rank == 1)

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
    def outcomes(self):
        # TODO Deprecated
        outcomes = {GameOutcomes.won: 0, GameOutcomes.lost: 0, GameOutcomes.drawn: 0, GameOutcomes.missing: 0}
        for t in self.teams:
            for g in t.games:
                outcomes[GameOutcomes.to_simple[g.outcome]] += 1
        return outcomes

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
                for x in range(self.finals_num_winners)
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
                data.append(max(0, s.num_teams + 1 - ceiling))
            else:
                data.append(max(0, t.season.num_teams + 1 - (t.finals_rank if t.finals_rank else ceiling)))
        return ', '.join(str(d) for d in data)


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
        return (
            self.regular_won + self.regular_forfeits_for,
            self.regular_drawn,
            self.regular_lost + self.regular_forfeits_against,
        )

    @cached_property
    def regular_record_str(self):
        return '-'.join(str(r) for r in self.regular_record)

    @cached_property
    def finals_record(self):
        return (
            sum(1 for gs in self.finals_games if gs.is_won),
            sum(1 for gs in self.finals_games if gs.is_drawn),  # Finals should not have draws, should they?
            sum(1 for gs in self.finals_games if gs.is_lost),
        )

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

    # @cached_property
    # def games_by_week(self):
    #     games = collections.OrderedDict()
    #     for game in self.games:
    #         if game.date_str not in games:
    #             games[game.date_str] = []
    #         games[game.date_str].append(game)
    #     return games


Season.default_order_by = [Season.first_week_date.asc(),]


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')

