from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String

from secret import DATABASE


Base = automap_base()

class User(Base):
    __tablename__ = 'users'
    is_active = True
    is_authenticated = True
    is_anonymous = False

    def __init__(self):
        Base.classes.users.__init__(self)

    def get_id(self):
        return self.id


engine = create_engine('sqlite:////' + DATABASE)
Base.prepare(engine, reflect=True)

db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))
Base.query = db_session.query_property()

Article = Base.classes.articles
History = Base.classes.histories

