import unicorn.db.connection
from unicorn.db.base import Base, Session
import unicorn.models

Base.metadata.create_all(unicorn.db.connection.engine)
Session.commit()
