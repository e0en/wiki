#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import secret


def get_db(g):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(secret.DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, g, args=(), one=False):
    cur = get_db(g).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


class Article(object):
    def __init__(self, g):
        self.g = g

    def filter_by(self, pagename):
        query_str = "SELECT * FROM wiki_article WHERE name='%s'" % pagename
        return query_db(query_str, self.g, one=True)

    def prev(self, pagename):
        prev_query = "SELECT name FROM wiki_article " + \
            "WHERE name<'%s' ORDER BY name desc LIMIT 1" % pagename
        return query_db(prev_query, self.g, one=True)

    def next(self, pagename):
        next_query = "SELECT name FROM wiki_article " + \
            "WHERE name>'%s' ORDER BY name LIMIT 1" % pagename
        return query_db(next_query, self.g, one=True)
