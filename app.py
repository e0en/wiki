#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import date, datetime

from flask import Flask, redirect, url_for, g, render_template, Response, request
from flask import send_from_directory
from flask_login import LoginManager, login_required
from flask_login import current_user
from flask_login import login_user, logout_user
from bcrypt import hashpw, checkpw

from parser import Parser
import latex
from models import Article, History, User, db_session
from secret import SECRET_KEY


login_manager = LoginManager()
app = Flask(__name__)

app.secret_key = SECRET_KEY
login_manager.init_app(app)
login_manager.login_view = 'login'

app.url_map.strict_slashes = False


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


@app.route('/login', methods=['POST', 'GET'])
def login():
    # if user is already logged in, redirect user
    if request.method == 'GET':
        return render_template('Login.html')
    else:
        user = User.query.filter(User.id == 0).first()
        hashed = user.hashed_pw.encode('utf-8')
        input_pw = request.form['password'].encode('utf-8')
        if checkpw(input_pw, hashed):
            login_user(user)
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/read/<pagename>')
def read(pagename):
    res = Article.query.filter(Article.name == pagename).first()
    parser = Parser()

    is_logged_in = current_user.is_authenticated

    if res is not None and (is_logged_in or res.is_public):
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
        return render_template('Read.html', article=res, prev_page=prev_page,
                               next_page=next_page)
    else:
        return redirect(url_for('search', q=pagename))


@app.route('/edit/<pagename>', methods=['POST', 'GET'])
@login_required
def edit(pagename):
    if request.method == 'POST':
        return process_edit(pagename, request.form, request.remote_addr)
    else:
        article = Article.query.filter_by(name=pagename).first()
        if article is None:
            article = Article(name=pagename, markdown='')
        return render_template('Edit.html', article=article)


def process_edit(pagename, form, ip_addr):
    content = form['content']
    now = datetime.now()

    article = Article.query.filter(Article.name == pagename).first()
    is_new_page = article is None

    if is_new_page:
        article = Article(name=pagename, time_create=now)

    is_public = form.get('is_public') is not None
    was_public = None if is_new_page else article.is_public == 1

    if article.content is not None:
        is_updated = article.content.strip() != content.strip()
    else:
        is_updated = True
    is_updated |= is_public != was_public

    if is_new_page or is_updated:
        article.content = content
        article.markdown = content
        article.ip_address = ip_addr
        article.content_html = Parser().parse_markdown(content)
        article.time_edit = now
        article.links = ''
        article.is_public = 1 if is_public else 0

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
                'is_public': article.is_public,
            }
            db_session.query(Article).\
                filter_by(name=pagename).\
                update(result_dict)

        db_session.add(h)
        db_session.commit()

    return redirect(url_for('read', pagename=pagename))


@app.route('/recentchanges')
def recentchanges():
    rows = History.query.order_by(History.time.desc()).all()
    h_list = []
    d_current = ''
    names_in_day = []
    title_list = []
    for r in rows:
        h = {}
        day = str(r.time).split(' ')[0]
        h['name'] = r.name
        h['name_esc'] = r.name
        h['time_edit'] = str(r.time).split(' ')[1].split('.')[0]
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
    return render_template('RecentChanges.html', history_list=h_list)


@app.route('/pagelist')
def pagelist():
    article_list = Article.query.\
        with_entities(Article.name).\
        order_by(Article.name).all()
    return render_template('PageList.html', article_list=article_list)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')

    query_obj = Article.query.\
        with_entities(Article.name).\
        filter_by(name=query)

    res = query_obj.first()

    if res:
        exact_match = res.name
    else:
        exact_match = None

    return render_template('Search.html', query=query, exact_match=exact_match)


@app.route('/history_list/<pagename>')
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
        return redirect(url_for('read', pagename=pagename))
    else:
        return render_template('HistoryList.html',
                               history_list=hlist,
                               article_name=pagename)


@app.route('/history/<history_id>')
def history(history_id):
    article = History.query.filter_by(id=history_id).first()

    if article is not None:
        parser = Parser()
        article.content_html = parser.parse_markdown(article.content)
        return render_template('History.html', article=article)
    else:
        return redirect(url_for('read', pagename=article.name))


@app.route('/delete/<pagename>')
@login_required
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


@app.route('/raw/<pagename>')
def raw(pagename):
    res = Article.query.filter(Article.name == pagename).first()
    if res is not None:
        return Response(res.markdown, mimetype='text/plain')
    else:
        return redirect(url_for('search', q=pagename))


@app.route('/jrnl')
@login_required
def jrnl():
    date_str = str(date.today())
    return redirect(url_for('edit', pagename=date_str))


@app.route('/')
def index():
    return redirect(url_for('read', pagename='MainPage'))


if __name__ == '__main__':
    app.run(debug=True)
