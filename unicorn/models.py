from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from unicorn.db.base import Base
from unicorn.values import SeasonStages


class Franchise(Base):
    __tablename__ = 'franchises'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    teams = relationship('Team', back_populates='franchise')


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
    st_position = Column(Integer)
    st_played = Column(Integer)
    st_won = Column(Integer)
    st_lost = Column(Integer)
    st_drawn = Column(Integer)
    st_forfeit_for = Column(Integer)
    st_forfeit_against = Column(Integer)
    st_score_for = Column(Integer)
    st_score_against = Column(Integer)
    st_score_difference = Column(Integer)
    st_bonus_points = Column(Integer)
    st_points = Column(Integer)

    @property
    def all_games(self):
        all = []
        all.extend(self.home_games)
        all.extend(self.away_games)
        return sorted(all, key=lambda g: g.starts_at, reverse=True)


Team.default_order_by = Team.name.asc(),


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    teams = relationship('Team', back_populates='season')


Season.default_order_by = Season.first_week_date.asc(),


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('seasons.id'))
    season = relationship('Season', back_populates='games')
    season_stage = Column(String(20), server_default=SeasonStages.regular)
    starts_at = Column(DateTime)
    home_team_id = Column(String(15), ForeignKey('teams.id'))
    home_team_score = Column(Integer)
    home_team_outcome = Column(String(5))
    home_team_points = Column(Integer)
    away_team_id = Column(String(15), ForeignKey('teams.id'))
    away_team_score = Column(Integer)
    away_team_outcome = Column(String(5))
    away_team_points = Column(Integer)
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

