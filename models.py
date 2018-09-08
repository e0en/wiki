from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base

from secret import DATABASE


# table_names = ['articles', 'histories', 'users']
table_names = ['articles', 'histories']


engine = create_engine('sqlite:////' + DATABASE)
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

metadata = MetaData()
metadata.reflect(engine, only=table_names)
Base = automap_base(metadata=metadata)
Base.query = db_session.query_property()
Base.prepare()


Article = Base.classes.articles
History = Base.classes.histories
# Users = Base.classes.users
