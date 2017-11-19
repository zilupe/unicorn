from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from unicorn.db.base import Base
from unicorn.values import SeasonStages


class Franchise(Base):
    __tablename__ = 'franchises'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(String(20))

    teams = relationship('Team', back_populates='franchise')

    @property
    def teams_sorted(self):
        return sorted(self.teams, key=lambda t: t.season.first_week_date)


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

    games = relationship('GameSide')


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


Season.default_order_by = Season.first_week_date.asc(),


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')

