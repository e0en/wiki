#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import quote
import re

import requests
from bs4 import BeautifulSoup


def load_oembed(url, api_url):
    full_url = api_url + 'url=' + quote(url)
    resp = requests.get(full_url).json()
    return resp['html']


def insert_oembeds(html):
    apis = []
    url = re.compile('https:\/\/(www\.|)twitter\.com\/.+?/status/.+')
    api_url = 'https://publish.twitter.com/oembed?dnt=true&hide_thread=true&'
    apis += [(url, api_url)]

    url = re.compile('https:\/\/(www\.|)youtube\.com\/watch\?v=.+')
    api_url = 'https://www.youtube.com/oembed?'
    apis += [(url, api_url)]

    doc = BeautifulSoup(html, 'html.parser')
    for a_tag in doc.find_all('a'):
        url = a_tag.get('href')
        if not url:
            continue
        for pattern, api_url in apis:
            if pattern.match(url):
                embed_html = load_oembed(url, api_url)
                new_tag = BeautifulSoup(embed_html, 'html.parser')
                a_tag.parent.insert_after(new_tag)
                break
    return str(doc)


if __name__ == '__main__':
    tw_url = 'https://twitter.com/Dispomanfaa/status/1041167900210487296'
    tw_api_url = 'https://publish.twitter.com/oembed?'
    print(load_oembed(tw_url, tw_api_url))

    html = '''
    <p>$$
    \mathbf X
    $$</p>
    <p>이 트윗을 봅니다. <a
    href="https://twitter.com/Dispomanfaa/status/1041167900210487296">https://twitter.com/Dispomanfaa/status/1041167900210487296</a>
    태풍은 무서운 것.</p>
    <p><a
    href="https://www.youtube.com/watch?v=PS5p9caXS4U">minutephysics</a>의
    비디오를 보자.</p>
    <h2>Backlinks</h2>
    <ul class="backlinks">
    <li><a class="link_inside" href="이옹위키문법">이옹위키문법</a></li>
    </ul>
    '''

    print(insert_oembeds(html))
