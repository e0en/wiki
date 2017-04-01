#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import date
from flask import redirect, url_for, g, render_template, Response, request

from __init__ import app
from parser import Parser
from models import Article, History


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/read/<pagename>")
def read(pagename):
    res = Article.query.filter(Article.name == pagename).first()
    parser = Parser()

    if res is not None:
        res.content_html = parser.parse_markdown(res.markdown)
        prev_page = Article.query\
            .filter(Article.name < pagename)\
            .order_by(Article.name.desc())\
            .first()
        next_page = Article.query\
            .filter(Article.name > pagename)\
            .order_by(Article.name)\
            .first()
        return render_template("Read.html", article=res, prev_page=prev_page,
                               next_page=next_page)
    else:
        return redirect(url_for('search', q=pagename))


@app.route("/edit/<pagename>", methods=["POST", "GET"])
def edit(pagename):
    if request.method == "POST":
        article = Article(name=pagename)
        return process_edit(article)
    else:
        article = Article.query.filter_by(name=pagename).first()
        if article is None:
            article = Article(name=pagename, markdown="")
        return render_template("Edit.html", article=article)


def process_edit(article):
    return redirect(url_for("read", pagename=article.name))


@app.route("/recentchanges")
def recentchanges():
    rows = History.query.order_by(History.time.desc()).all()
    h_list = []
    d_current = ''
    names_in_day = []
    title_list = []
    for r in rows:
        h = {}
        day = str(r.time).split(" ")[0]
        h['name'] = r.name
        h['name_esc'] = r.name
        h['time_edit'] = str(r.time).split(" ")[1].split(".")[0]
        h['ip_address'] = r.ip_address
        h['type'] = r.type
        if r.name in title_list:
            continue
        else:
            title_list.append(r.name)
        if d_current == '':
            d_current = day
            tmp = {'date': d_current, 'changes': [h]}
            names_in_day.append(r.name + ',' + r.type)
        elif d_current != day:
            h_list.append(tmp)
            tmp = {'date': day, 'changes': [h]}
            names_in_day.append(r.name + ',' + r.type)
            d_current = day
        elif r.name + ',' + r.type not in names_in_day:
            tmp['changes'].append(h)
            names_in_day.append(r.name + ',' + r.type)
    h_list.append(tmp)
    return render_template("RecentChanges.html", history_list=h_list)


@app.route("/pagelist")
def pagelist():
    article_list = Article.query.\
        with_entities(Article.name).\
        order_by(Article.name).all()
    return render_template("PageList.html", article_list=article_list)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    dirname = os.path.dirname(os.path.realpath(__file__)) +\
            "/static/upload"
    filenames = [x for x in os.listdir(dirname) if x not in {".", ".."}]
    return render_template("Upload.html", filenames=filenames)


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('q', '')
    res = Article.query.\
        with_entities(Article.name).\
        filter_by(name=query).first()

    if res:
        exact_match = res.name
    else:
        exact_match = None

    return render_template("Search.html", query=query, exact_match=exact_match)


@app.route("/history_list/<pagename>")
def history_list(pagename):
    # fetch history of the page of the given name
    try:
        hlist = History.query.\
                filter(History.type != 'new').\
                filter(History.name == pagename).\
                order_by(History.id.desc()).all()
    except:
        hlist = []

    if len(hlist) == 0:
        return redirect(url_for("read", pagename=pagename))
    else:
        return render_template("HistoryList.html",
                               history_list=hlist,
                               article_name=pagename)


@app.route("/history/<history_id>")
def history(history_id):
    article = History.query.filter_by(id=history_id).first()

    if article is not None:
        parser = Parser()
        article.content_html = parser.parse_markdown(article.content)
        return render_template("History.html", article=article)
    else:
        return redirect(url_for("read", pagename=article.name))


@app.route("/delete/<pagename>")
def delete(pagename):
    return "delete"


@app.route("/raw/<pagename>")
def raw(pagename):
    res = Article.query.filter(Article.name == pagename).first()
    if res is not None:
        return Response(res.markdown, mimetype="text/plain")
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
