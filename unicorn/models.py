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
        return sum(1 for t in self.teams if t.fin_position == 1)


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
    reg_position = Column(Integer)
    reg_played = Column(Integer)
    reg_won = Column(Integer)
    reg_lost = Column(Integer)
    reg_drawn = Column(Integer)
    reg_forfeits_for = Column(Integer)
    reg_forfeits_against = Column(Integer)
    reg_score_for = Column(Integer)
    reg_score_against = Column(Integer)
    reg_score_difference = Column(Integer)
    reg_bonus_points = Column(Integer)
    reg_points = Column(Integer)

    # Finals aggregates
    fin_position = Column(Integer)

    games = relationship('GameSide')

    @property
    def proud_name(self):
        if self.franchise.name:
            if self.name != self.franchise.name:
                return '{}*'.format(self.franchise.name)
        return self.name


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

    @property
    def is_over(self):
        return self.finals_champions.fin_position == 1

    @property
    def teams_regular_order(self):
        return sorted(self.teams, key=lambda t: t.reg_position or 100)

    @property
    def regular_champions(self):
        return self.teams_regular_order[0]

    @property
    def teams_finals_order(self):
        return sorted(self.teams, key=lambda t: t.fin_position or 100)

    @property
    def finals_champions(self):
        return self.teams_finals_order[0]

    @property
    def date_range_str(self):
        return '{} - {}'.format(
            self.first_week_date.strftime('%d/%m/%Y'),
            self.last_week_date.strftime('%d/%m/%Y'),
        )


Season.default_order_by = Season.first_week_date.asc(),


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')

