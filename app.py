#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, date
from flask import Flask, redirect, url_for, g, render_template


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
        print res.keys()
        return render_template("Read.html", article=res)
    else:
        return redirect(url_for('search', q=pagename))


@app.route("/edit/<pagename>")
def edit(pagename):
    query_str = "SELECT * FROM wiki_article WHERE name='%s'" % pagename
    article = query_db(query_str, one=True)

    if article is None:
        article = { "name": pagename }
    return render_template("Edit.html", article=article)


@app.route("/recentchanges")
def recentchanges():
    return render_template("RecentChanges.html")


@app.route("/pagelist")
def pagelist():
    query_str = "SELECT name FROM wiki_article ORDER BY name"
    article_list = query_db(query_str)
    return render_template("PageList.html", article_list=article_list)


@app.route("/upload")
def upload():
    return render_template("Upload.html")


@app.route("/search")
def search():
    return render_template("Search.html")


@app.route("/history_list/<pagename>")
def history_list(pagename):
    return "history_list"


@app.route("/delete/<pagename>")
def delete(pagename):
    return "delete"


@app.route("/raw/<pagename>")
def raw(pagename):
    query_str = "SELECT * FROM wiki_article WHERE name='%s'" % pagename
    res = query_db(query_str, one=True)

    if res is not None:
        return render_template("Read.html")
        return res["markdown"]
    else:
        return redirect(url_for('search', q=pagename))


@app.route("/jrnl")
def jrnl():
    date_str = str(date.today())
    return redirect(url_for("edit", pagename=date_str))


@app.route("/")
def index():
    return redirect(url_for('read', pagename='MainPage'))


if __name__ == '__main__':
    app.run(debug=True)
