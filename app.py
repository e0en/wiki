#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date, datetime

from flask import Flask, g, Response, request
from flask import redirect, url_for, render_template
from flask import send_from_directory
from flask_login import LoginManager, login_required
from flask_login import current_user
from flask_login import login_user, logout_user
from bcrypt import checkpw
from sqlalchemy.sql.expression import func

from oembed import insert_oembeds
from parser import Parser
from models import Article, History, User, Link, db_session
from secret import SECRET_KEY
from utils import to_url_name


login_manager = LoginManager()
app = Flask(__name__)

app.secret_key = SECRET_KEY
login_manager.init_app(app)
login_manager.login_view = 'login'

app.url_map.strict_slashes = False


def get_pages():
    if current_user.is_authenticated:
        return Article.query
    else:
        return Article.query.filter(Article.is_public == 1)


def get_user_ip():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For']
    else:
        return request.remote_addr


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
            login_user(user, remember=True)
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
    is_logged_in = current_user.is_authenticated

    if res is None:
        res = Article.query.filter(Article.url_name == pagename).first()
    if res is None:
        return redirect(url_for('search', q=pagename))
    if not res.is_public and not is_logged_in:
        return app.login_manager.unauthorized()

    prev_page = get_pages().filter(Article.name < pagename)\
        .order_by(Article.name.desc())\
        .first()
    next_page = get_pages()\
        .filter(Article.name > pagename)\
        .order_by(Article.name)\
        .first()
    body = render_template('Read.html', article=res,
                           prev_page=prev_page,
                           next_page=next_page)
    t_edit = res.time_edit.strftime('%a, %d %b %Y %H:%M:%S GMT')
    resp = Response(body)
    resp.headers['Last-Modified'] = t_edit
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/random')
def random():
    res = get_pages().order_by(func.random()).first()
    return redirect(url_for('read', pagename=res.name))


@app.route('/edit/<pagename>', methods=['POST', 'GET'])
@login_required
def edit(pagename):
    if request.method == 'POST':
        ip_address = get_user_ip()
        return process_edit(pagename, request.form, ip_address)
    else:
        article = Article.query.filter_by(name=pagename).first()
        if article is None:
            article = Article(name=pagename, content='')
            article.time_edit = datetime.now()
        if article.url_name is None:
            article.url_name = to_url_name(pagename)

        t_edit = article.time_edit.strftime('%a, %d %b %Y %H:%M:%S GMT')
        body = render_template('Edit.html', article=article)
        resp = Response(body)
        resp.headers['Last-Modified'] = t_edit
        resp.headers['Cache-Control'] = 'no-cache'
        return resp


def process_edit(pagename, form, ip_addr):
    url_name = form['url_name']
    content = form['content'].strip()
    is_public = form.get('is_public', False)
    now = datetime.now()

    article = Article.query.filter(Article.name == pagename).first()
    is_new_page = article is None

    if is_new_page:
        article = Article(name=pagename, time_create=now)
    is_updated = is_article_updated(article, form)
    if not (is_new_page or is_updated):
        return redirect(url_for('read', pagename=pagename))

    article.url_name = url_name
    article.content = content
    article.ip_address = ip_addr

    article.html, links = parse_content(pagename, content)
    article.time_edit = now
    article.links = ''
    article.is_public = 1 if is_public else 0

    all_names = Article.query.with_entities(Article.name).all()
    all_names = [x.name for x in all_names]
    existing_links = Link.query.filter_by(from_name=pagename).all()
    for l in existing_links:
        db_session.delete(l)
    db_session.commit()

    added_names = set()
    for l in links:
        if l in all_names and l not in added_names:
            new_link = Link(from_name=pagename, to_name=l)
            added_names.add(l)
            db_session.add(new_link)

    add_history(article, is_new_page)
    return redirect(url_for('read', pagename=pagename))


def add_history(article, is_new_page):
    pagename = article.name
    content = article.content
    ip_addr = article.ip_address
    now = datetime.now()
    h = History(name=pagename, content=content, ip_address=ip_addr, time=now)
    if is_new_page:
        h.type = 'new'
        db_session.add(article)
    else:
        h.type = 'mod'
        result_dict = {
            'url_name': article.url_name,
            'content': article.content,
            'html': article.html,
            'time_edit': article.time_edit,
            'is_public': article.is_public,
        }
        db_session.query(Article).filter_by(name=pagename).update(result_dict)
    db_session.add(h)
    db_session.commit()


@app.route('/preview/<pagename>', methods=['POST', 'GET'])
@login_required
def preview(pagename):
    content = request.form['content']
    html, _ = parse_content(pagename, content)
    body = render_template('Preview.html', pagename=pagename, content=html)
    resp = Response(body)
    return resp


@app.route('/recentchanges')
@login_required
def recentchanges():
    rows = History.query.order_by(History.time.desc()).all()
    all_names = set([x[0] for x in db_session.query(Article.name).all()])
    print(all_names)
    h_list = []
    d_current = ''
    names_in_day = []
    title_list = []
    for r in rows:
        if r.name not in all_names:
            continue
        h = {}
        day = str(r.time).split(' ')[0]
        h['name'] = r.name
        h['name_esc'] = r.name
        h['time_edit'] = str(r.time).split(' ')[1].split('.')[0]
        h['ip_address'] = r.ip_address
        h['type'] = r.type
        if h['type'] == 'del':
            continue
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
    article_list = get_pages().\
        with_entities(Article.name).\
        order_by(Article.name).all()
    return render_template('PageList.html', article_list=article_list)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')

    matches = get_pages().\
        with_entities(Article.name).\
        filter(Article.name.like(f'%{query}%')).\
        all()
    matches = [x.name for x in matches]
    exact_match = [a for a in matches if a == query]

    if exact_match:
        exact_match = exact_match[0]
    else:
        exact_match = None

    return render_template('Search.html',
                           query=query,
                           exact_match=exact_match,
                           match_list=matches)


@app.route('/history_list/<pagename>')
def history_list(pagename):
    # fetch history of the page of the given name
    hlist = History.query.\
        filter(History.type != 'new').\
        filter(History.name == pagename).\
        order_by(History.id.desc()).all()

    if len(hlist) == 0:
        return redirect(url_for('read', pagename=pagename))
    else:
        return render_template('HistoryList.html',
                               history_list=hlist,
                               article_name=pagename)


@app.route('/history/<history_id>')
@login_required
def history(history_id):
    article = History.query.filter_by(id=history_id).first()
    if article is not None:
        article.html, _ = parse_content(article.name, article.content)
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
                    ip_address=get_user_ip(),
                    time=datetime.now(),
                    type='del')
        db_session.add(h)
        Article.query.filter(Article.name == pagename).delete()
        db_session.commit()

    return redirect(url_for('read', pagename='MainPage'))


@app.route('/raw/<pagename>')
@login_required
def raw(pagename):
    res = Article.query.filter(Article.name == pagename).first()
    if res is not None:
        return Response(res.content, mimetype='text/plain')
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


def is_article_updated(article, form):
    url_name = form['url_name']
    content = form['content']

    is_public = form.get('is_public') is not None
    was_public = article.is_public == 1

    if article.content is not None:
        is_updated = article.content.strip() != content.strip()
    else:
        is_updated = True
    if article.url_name is None or article.url_name.strip() != url_name:
        is_updated = True

    return is_updated or (is_public != was_public)


def parse_content(pagename, content):
    parser = Parser()
    html = parser.parse_markdown(content)
    html = insert_oembeds(html)

    backlinks = Link.query.filter_by(to_name=pagename).all()
    backlinks = [l.from_name for l in backlinks]
    html += parser.gen_backlink_html(backlinks)
    return html, parser.wiki_links


if __name__ == '__main__':
    app.run(debug=True)
