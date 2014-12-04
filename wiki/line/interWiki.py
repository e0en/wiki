import wiki.models as wikiModels
from wiki import wikiMisc


def loadInterWiki(wiki_nick):
    a = wikiModels.Article.objects.get(name='InterWiki')
    s = a.content.strip().split('\n')
    for i in range(0, len(s)):
        tmp = s[i].strip()[1:]
        tmp = tmp.split(',', 3)
        if tmp[1].strip() == wiki_nick:
            return tmp[0].strip(), tmp[2].strip(), tmp[3].strip()


def parse(text, acc):
    content = text.split(':')
    wiki_nick = content[0].strip()
    wiki_page = content[1].strip()

    wiki_name, wiki_addr, wiki_favicon = loadInterWiki(wiki_nick)
    wiki_addr = wiki_addr % wiki_page
    result = \
        '<img src="%s" style="border: 1px #ccc solid;" alt="%s" /> <a href="%s">%s</a>'\
        % (wiki_favicon, wiki_name, wikiMisc.escapeHTML(wiki_addr), wiki_page)
    return result
