#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import date
from flask import redirect, url_for, g, render_template, Response, request

from __init__ import app
from parser import Parser
import model as M


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/read/<pagename>")
def read(pagename):
    res = M.Article().filter_by(pagename=pagename)
    parser = Parser()

    if res is not None:
        res = dict(res)
        res['content_html'] = parser.parse_markdown(res['markdown'])
        prev_page = M.Article().prev(pagename)
        next_page = M.Article().next(pagename)
        return render_template("Read.html", article=res, prev_page=prev_page,
                               next_page=next_page)
    else:
        return redirect(url_for('search', q=pagename))


@app.route("/edit/<pagename>", methods=["POST", "GET"])
def edit(pagename):
    if request.method == "POST":
        return process_edit(article)
    else:
        article = M.Article().filter_by(pagename=pagename)
        if article is None:
            article = {"name": pagename}
        return render_template("Edit.html", article=article)


def process_edit(article):
    return redirect(url_for("read", pagename=article["name"]))


@app.route("/recentchanges")
def recentchanges():
    query = "SELECT * FROM wiki_history ORDER BY time desc"
    histlist = M.query_db(query)
    hlist = []
    d_current = ''
    names_in_day = []
    titlelist = []
    for item in histlist:
        h = {}
        day = item["time"].split(" ")[0]
        h['name'] = item["name"]
        h['name_esc'] = item["name"]
        h['time_edit'] = item["time"].split(" ")[1].split(".")[0]
        h['ip_address'] = item["ip_address"]
        h['type'] = item["type"]
        if item["name"] in titlelist:
            continue
        else:
            titlelist.append(item["name"])
        if d_current == '':
            d_current = item["time"].split(" ")[0]
            tmp = {'date': d_current, 'changes': [h]}
            names_in_day.append(item["name"] + ',' + item["type"])
        elif d_current != day:
            hlist.append(tmp)
            tmp = {'date': day, 'changes': [h]}
            names_in_day.append(item["name"] + ',' + item["type"])
            d_current = day
        elif item["name"] + ',' + item["type"] not in names_in_day:
            tmp['changes'].append(h)
            names_in_day.append(item["name"] + ',' + item["type"])
    hlist.append(tmp)
    return render_template("RecentChanges.html", history_list=hlist)


@app.route("/pagelist")
def pagelist():
    query_str = "SELECT name FROM wiki_article ORDER BY name"
    article_list = M.query_db(query_str)
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
    query_str = "SELECT name FROM wiki_article WHERE name='%s'" % query
    res = M.query_db(query_str, one=True)
    if res:
        exact_match = res["name"]
    else:
        exact_match = None

    return render_template("Search.html", query=query, exact_match=exact_match)


@app.route("/history_list/<pagename>")
def history_list(pagename):
    # fetch history of the page of the given name
    try:
        query = "SELECT * FROM wiki_history " + \
            "WHERE name='%s' AND type<>'new' ORDER BY id DESC" % pagename
        hlist = M.query_db(query)
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
    query = "SELECT * FROM wiki_history WHERE id=%s" % history_id
    article = M.query_db(query, one=True)

    if article is not None:
        parser = Parser()
        history = dict(article)
        history["content_html"] = parser.parse_markdown(article["content"])
        print(history)
        return render_template("History.html", article=history)
    else:
        return redirect(url_for("read", pagename=article["name"]))


@app.route("/delete/<pagename>")
def delete(pagename):
    return "delete"


@app.route("/raw/<pagename>")
def raw(pagename):
    res = M.Article().filter_by(pagename)
    if res is not None:
        return Response(res["markdown"], mimetype="text/plain")
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
