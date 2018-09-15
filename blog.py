#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, g, Response, request
from flask import redirect, url_for, render_template
from flask import send_from_directory

from models import Article
from secret import SECRET_KEY


app = Flask(__name__)

app.secret_key = SECRET_KEY

app.url_map.strict_slashes = False


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


def query_post(pagename):
    return Article.query.\
        filter(Article.is_public == 1).\
        filter(Article.name.like(f'blog:{pagename}%')).\
        order_by(Article.time_create.desc())


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/<pagename>')
def read(pagename):
    res = query_post(pagename).first()

    if res is not None and res.is_public:
        if res.name[5:] != pagename:
            return redirect(url_for('read', pagename=res.name[5:]))
        body = render_template('blog.html', article=res)
        t_edit = res.time_edit.strftime('%a, %d %b %Y %H:%M:%S GMT')
        resp = Response(body)
        resp.headers['Last-Modified'] = t_edit
        return resp
    else:
        return redirect(url_for('archive'))


@app.route('/archive')
def archive():
    article_list = query_post('').all()
    article_list = [a.name[5:] for a in article_list]
    return render_template('blog_archive.html', article_list=article_list)


@app.route('/')
def index():
    page = query_post('').first()
    if page:
        return redirect(url_for('read', pagename=page.name[:5]))
    else:
        return redirect(url_for('archive'))


if __name__ == '__main__':
    app.run(debug=True)
