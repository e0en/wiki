from datetime import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, DateTime, Text,\
    ForeignKey

from database import Base


history_authors = Table(
    'wiki_history_author', Base.metadata,
    Column('author_id', Integer, ForeignKey('wiki_authors.id')),
    Column('history_id', Integer))
    )


class Author(Base):
    __tablename__ = 'wiki_author'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    password = Column(String(16))
    email = Column(String(100))


class Article(Base):
    __tablename__ = 'wiki_article'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    ip_address = Column(String(32))
    content = Column(Text)
    markdown = Column(Text)
    content_html = Column(Text)
    time_create = Column(DateTime, default=datetime.now)
    time_edit = Column(DateTime, default=datetime.now,
            onupdate=datetime.now)
    links = Column(Text, default='')


class Media(Base):
    __tablename__ = 'wiki_media'
    id = Column(Integer, primary_key=True)
    filename = Column(String(256))
    time_create = Column(DateTime, default=datetime.now,
            onupdate=datetime.now)


class History(Base):
    __tablename__ = 'wiki_history'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    ip_address = Column(String(32))

    author = relationship("Author", secondary=history_authors)
    content = Column(Text, default='')
    time = Column(DateTime, onupdate=datetime.now)
    type = Column(String(16), default='mod')
