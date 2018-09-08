#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import date, datetime
from flask import Flask, redirect, url_for, g, render_template, Response, request
from flask import send_from_directory
from flask_login import LoginManager

from parser import Parser
import latex
from models import Article, History, db_session


login_manager = LoginManager()
app = Flask(__name__)
login_manager.init_app(app)
app.url_map.strict_slashes = False


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


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
        processed = latex.preprocess(res.markdown)
        res.content_html = parser.parse_markdown(processed)
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
        return process_edit(pagename, request.form, request.remote_addr)
    else:
        article = Article.query.filter_by(name=pagename).first()
        if article is None:
            article = Article(name=pagename, markdown="")
        return render_template("Edit.html", article=article)


def process_edit(pagename, form, ip_addr):
    content = form['content']
    now = datetime.now()

    article = Article.query.filter(Article.name == pagename).first()
    is_new_page = article is None
    if is_new_page:
        article = Article(name=pagename, time_create=now)

    if is_new_page or article.content.strip() != content.strip():
        article.content = content
        article.markdown = content
        article.ip_address = ip_addr
        article.content_html = Parser().parse_markdown(content)
        article.time_edit = now
        article.links = ''

        h = History(name=pagename, content=content, ip_address=ip_addr,
                    time=now)

        if is_new_page:
            h.type = 'new'
            db_session.add(article)
        else:
            h.type = 'mod'
            result_dict = {
                'content': article.content,
                'markdown': article.markdown,
                'ip_address': article.ip_address,
                'content_html': article.content_html,
                'links': article.links,
                'time_edit': article.time_edit,
            }
            db_session.query(Article).\
                filter_by(name=pagename).\
                update(result_dict)

        db_session.add(h)
        db_session.commit()

    return redirect(url_for("read", pagename=pagename))


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
    article = Article.query.filter(Article.name == pagename).first()
    if article is not None:
        h = History(name=pagename,
                    content=article.content,
                    ip_address=request.remote_addr,
                    time=datetime.now(),
                    type='del')
        db_session.add(h)
        Article.query.filter(Article.name == pagename).delete()
        db_session.commit()

    return redirect(url_for('read', pagename='MainPage'))


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
