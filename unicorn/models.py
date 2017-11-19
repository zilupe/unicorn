from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from unicorn.core.utils import cached_property
from unicorn.db.base import Base
from unicorn.values import SeasonStages, GameOutcomes


class Franchise(Base):
    __tablename__ = 'franchises'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(String(20))

    teams = relationship('Team', back_populates='franchise')

    @cached_property
    def teams_sorted(self):
        return sorted(self.teams, key=lambda t: t.season.first_week_date)

    @cached_property
    def outcomes(self):
        outcomes = {GameOutcomes.won: 0, GameOutcomes.lost: 0, GameOutcomes.drawn: 0, GameOutcomes.missing: 0}
        for t in self.teams:
            for g in t.games:
                outcomes[GameOutcomes.to_simple[g.outcome]] += 1
        return outcomes

    @cached_property
    def num_titles(self):
        return sum(1 for t in self.teams if t.finals_rank == 1)


Franchise.default_order_by = Franchise.name.asc(),


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

    @property
    def proud_name(self):
        if self.franchise.name:
            if self.name != self.franchise.name:
                return '{}*'.format(self.franchise.name)
        return self.name

    @property
    def regular_games(self):
        return [gs for gs in self.games if gs.game.is_regular]

    @cached_property
    def regular_num_games_decided(self):
        return sum(1 for gs in self.regular_games if gs.is_decided)

    @cached_property
    def regular_score_for_avg(self):
        if not self.regular_num_games_decided:
            return 0
        return sum(gs.score for gs in self.regular_games if gs.is_decided) / self.regular_num_games_decided

    @cached_property
    def regular_score_against_avg(self):
        if not self.regular_num_games_decided:
            return 0
        return sum(gs.opponent.score for gs in self.regular_games if gs.is_decided) / self.regular_num_games_decided

    @cached_property
    def regular_score_difference_avg(self):
        if not self.regular_num_games_decided:
            return 0
        return self.regular_score_difference / self.regular_num_games_decided

    @cached_property
    def regular_points_avg(self):
        if not self.regular_num_games_decided:
            return 0
        return self.regular_points / self.regular_num_games_decided

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
    def finals_games(self):
        return [gs for gs in self.games if not gs.game.is_regular]

    @cached_property
    def finals_score_for_avg(self):
        if not self.finals_num_games_decided:
            return 0
        return sum(gs.score for gs in self.finals_games if gs.is_decided) / self.finals_num_games_decided

    @cached_property
    def finals_score_against_avg(self):
        if not self.finals_num_games_decided:
            return 0
        return sum(gs.opponent.score for gs in self.finals_games if gs.is_decided) / self.finals_num_games_decided

    @cached_property
    def finals_score_difference(self):
        return sum(gs.score - gs.opponent.score for gs in self.finals_games if gs.is_decided)

    @cached_property
    def finals_score_difference_avg(self):
        if not self.finals_num_games_decided:
            return 0
        return self.finals_score_difference / self.finals_num_games_decided

    @cached_property
    def finals_num_games_decided(self):
        return sum(1 for gs in self.finals_games if gs.is_decided)

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


Team.default_order_by = Team.name.asc(),


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)

    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season', back_populates='games')

    season_stage = Column(String(20), server_default=SeasonStages.regular)
    starts_at = Column(DateTime)
    notes = Column(Text)

    sides = relationship('GameSide', back_populates='game')

    @property
    def is_regular(self):
        return self.season_stage == SeasonStages.regular

    @property
    def home_side(self):
        return self.sides[0]

    @property
    def away_side(self):
        return self.sides[1]

    @property
    def date_str(self):
        return self.starts_at.strftime('%d/%m/%Y')

    @property
    def time_str(self):
        return self.starts_at.strftime('%H:%M')

    @cached_property
    def score_link(self):
        return '<a href="{}">{} - {}</a>'.format(
            self.simple_url,
            self.home_side.score,
            self.away_side.score,
        )


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

    @property
    def opponent(self):
        for side in self.game.sides:
            if side != self:
                return side


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    teams = relationship('Team', back_populates='season')

    @cached_property
    def first_week_date_str(self):
        return self.first_week_date.strftime('%d/%m/%Y')

    @cached_property
    def last_week_date_str(self):
        return self.last_week_date.strftime('%d/%m/%Y')

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


Season.default_order_by = Season.first_week_date.asc(),


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')

