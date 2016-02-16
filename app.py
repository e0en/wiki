#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from flask import Flask, redirect, url_for, g


app = Flask(__name__)


DATABASE = 'e0enwiki.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/read/<pagename>")
def read(pagename):
    query_str = "SELECT * FROM wiki_article WHERE name='%s'" % pagename
    res = query_db(query_str, one=True)

    if res is not None:
        return "<pre>%s</pre>" % res["markdown"]
    else:
        return redirect(url_for('search', q=pagename))


@app.route("/edit/<pagename>")
def edit(pagename):
    query_str = "SELECT * FROM wiki_article WHERE name='%s'" % pagename
    old = query_db(query_str, one=True)

    if old is not None:
        return "edit %s" % pagename
    else:
        return "create %s" % pagename


@app.route("/search/<q>")
def search(q):
    return "search %s" % q


@app.route("/")
def index():
    return redirect(url_for('read', pagename='MainPage'))


if __name__ == '__main__':
    app.run(debug=True)
