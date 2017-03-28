from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base

from secret import DATABASE


table_names = [
    'wiki_author',
    'wiki_article',
    'wiki_media',
    'wiki_history',
    'wiki_history_author'
]


engine = create_engine('sqlite:////' + DATABASE)
db_session = scoped_session(sessionmaker(bind=engine))

metadata = MetaData()
metadata.reflect(engine, only=table_names)
Base = automap_base(metadata=metadata)
Base.query = db_session.query_property()
Base.prepare()


Author = Base.classes.wiki_author
Article = Base.classes.wiki_article
Media = Base.classes.wiki_media
History = Base.classes.wiki_history
HistoryAuthor = Base.classes.wiki_history_author
