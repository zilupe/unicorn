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
        return '<a href="/team_{}.html">{}</a>'.format(self.id, self.name)


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.name)


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
        return '<{} {} vs {}>'.format(self.__class__.__name__, self.home_team, self.away_team)


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')
Team.home_games = relationship('Game', foreign_keys=Game.home_team_id, order_by=Game.starts_at, back_populates='home_team')
Team.away_games = relationship('Game', foreign_keys=Game.away_team_id, order_by=Game.starts_at, back_populates='away_team')
