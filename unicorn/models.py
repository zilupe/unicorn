from sqlalchemy import Column, create_engine, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    def __str__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.name)


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    first_week_date = Column(Date)
    last_week_date = Column(Date)

    def __str__(self):
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

    def __str__(self):
        return '<{} {} vs {}>'.format(self.__class__.__name__, self.home_team, self.away_team)


Season.games = relationship('Game', order_by=Game.starts_at, back_populates='season')
Team.home_games = relationship('Game', foreign_keys=Game.home_team_id, order_by=Game.starts_at, back_populates='home_team')
Team.away_games = relationship('Game', foreign_keys=Game.away_team_id, order_by=Game.starts_at, back_populates='away_team')


engine = create_engine('sqlite://')
Session = sessionmaker()


Base.metadata.create_all(engine)

Session.configure(bind=engine)

season1 = Season(id=1, name='Winter 2010')
lost_angels = Team(id=1, name='Lost Angels')
camden_hells = Team(id=2, name='Camden Hells')

session = Session()
session.add(season1)
session.add(lost_angels)
session.add(camden_hells)

game1 = Game(id=1, season=season1, home_team=lost_angels, away_team=camden_hells)
session.add(game1)

session.commit()

games = session.query(Game).all()
g = games[0]

print(g)
print(g.home_team)
print(g.away_team)



