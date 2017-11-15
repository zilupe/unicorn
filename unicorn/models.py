from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from unicorn.db.base import Base


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.name)

    @property
    def link(self):
        return '<a href="team_{}.html">{}</a>'.format(self.id, self.name)

    @property
    def all_games(self):
        all = []
        all.extend(self.home_games)
        all.extend(self.away_games)
        return sorted(all, key=lambda g: g.starts_at, reverse=True)

    @property
    def all_seasons(self):
        seasons = set(g.season for g in self.all_games)
        return sorted(seasons, key=lambda s: s.first_week_date)


Team.default_order_by = Team.name.asc(),


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.name)

    @property
    def link(self):
        return '<a href="season_{}.html">{}</a>'.format(self.id, self.name)


Season.default_order_by = Season.first_week_date.asc(),


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season', back_populates='games')
    starts_at = Column(DateTime)
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    home_team_points = Column(Integer)
    home_team_outcome = Column(Integer)
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_points = Column(Integer)
    away_team_outcome = Column(Integer)
    stage = Column(String(20), server_default='regular')
    notes = Column(Text)

    home_team = relationship('Team', foreign_keys=[home_team_id], back_populates='home_games')
    away_team = relationship('Team', foreign_keys=[away_team_id], back_populates='away_games')

    def __repr__(self):
        return '<{} {} - {}>'.format(self.__class__.__name__, self.home_team, self.away_team)

    @property
    def name(self):
        return '{} - {}'.format(self.home_team.name, self.away_team.name)

    @property
    def link(self):
        return '<a href="game_{}.html">{}</a>'.format(self.id, self.name)


Game.default_order_by = Game.starts_at.asc(),


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')
Team.home_games = relationship('Game', foreign_keys=Game.home_team_id, order_by=Game.starts_at, back_populates='home_team')
Team.away_games = relationship('Game', foreign_keys=Game.away_team_id, order_by=Game.starts_at, back_populates='away_team')
