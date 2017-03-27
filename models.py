from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

from database import engine


table_names = [
    'wiki_author',
    'wiki_article',
    'wiki_media',
    'wiki_history',
    'wiki_history_author'
]

metadata = MetaData()
metadata.reflect(engine, only=table_names)
Base = automap_base(metadata=metadata)
Base.prepare()


Author = Base.classes.wiki_author
Article = Base.classes.wiki_article
Media = Base.classes.wiki_media
History = Base.classes.wiki_history
HistoryAuthor = Base.classes.wiki_history_author
