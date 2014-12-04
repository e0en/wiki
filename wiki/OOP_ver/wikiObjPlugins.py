import wikiSettings
import wikiMisc
import urllib
import re
import wiki.models as wikiModels
import inline
from wikiArticleObject import WikiElem


def load():
    plugins = []

    # order DOES matter.
    plugins = [CarrageReturn(), SpecialChar(), InlineCode(), Strike(),
               LinkMaker(), InlineLaTeX(), UrlLinker(), Emphasize(),
               InlineQuote()]

    return plugins


def extractContent(text, idx, tag_front, tag_back):
    pos_start = idx + len(tag_front)
    pos_end = pos_start + text[pos_start:].find(tag_back)
    content = text[pos_start:pos_end]
    return (content, pos_end + len(tag_back) - idx)


def findTag(text, idx, tag_front, tag_back):
    return text[idx:idx + len(tag_front)] == tag_front and text[idx + len(tag_front):].find(tag_back) != -1


class Plugin:

    def test(self, text, idx):
        return False

    def parse(self, text, idx, page):
        return None, 1


class CarrageReturn(Plugin):

    def test(self, text, idx):
        return text[idx] == '\n'

    def parse(self, text, idx, page):
        return WikiElem(eType='br'), 1


class SpecialChar(Plugin):

    def test(self, text, idx):
        if text[idx] == '\\':
            return True
        else:
            return False

    def parse(self, text, idx, acc):
        special_chars = ['$', '[', ']', '\\']
        if text[idx + 1] in special_chars:
            return WikiElem(eType='plain', value=text[idx + 1]), 2
        else:
            return WikiElem(eType='plain', value='\\'), 1


class InlineQuote(Plugin):

    def test(self, text, idx):
        p = re.compile('"([^"]+)" *\(([^()]+)\)')
        m = p.match(text[idx:])
        if m == None:
            return False
        else:
            self.content = m.group(1)
            self.src = m.group(2)
            self.length = len(m.group(0))
            return True

    def parse(self, text, idx, acc):
        if wikiMisc.isURI(self.src):
            v = {'src': self.src, 'uri': self.src, 'content': self.content}
        else:
            v = {'src': self.src, 'content': self.content}
        parsed = WikiElem(eType='q', value=v)
        return parsed, self.length


class InlineCode(Plugin):

    def test(self, text, idx):
        return findTag(text, idx, '[[code:', ']]')

    def parse(self, text, idx, acc):
        (content, shift) = extractContent(text, idx, '[[code:', ']]')
        return ('<code>' + content + '</code>', shift)


class Emphasize(Plugin):

    def test(self, text, idx):
        if text[idx:idx + 2] == "''":
            return True
        else:
            return False

    def parse(self, text, idx, acc):
        for i in range(idx, len(text)):
            if text[i] != "'":
                pos_no_mark = i
                break
            else:
                pos_no_mark = len(text) - 1
        pos_end_mark = text[pos_no_mark:].find("''")

        if pos_end_mark == -1:
            return ("''", 2)
        else:
            pos_end_mark += pos_no_mark
            for i in range(pos_end_mark, len(text)):
                if text[i] != "'":
                    idx_end = i
                    break
                elif i == len(text) - 1:
                    idx_end = i + 1
                    break

            txt = text[idx:idx_end]
            n_mark = 0
            for i in range(0, len(txt)):
                if txt[0] == txt[-1] == "'":
                    txt = txt[1:-1]
                    n_mark += 1
                    if n_mark >= 3:
                        break
                else:
                    break

            if n_mark == 2:
                return '<em>' + txt + '</em>', idx_end - idx
            elif n_mark == 3:
                return '<strong>' + txt + '</strong>', idx_end - idx
            else:
                # print txt
                return txt, idx_end - idx


class Strike(Plugin):

    def test(self, text, idx):
        return findTag(text, idx, '--', '--')

    def parse(self, text, idx, acc):
        (content, shift) = extractContent(text, idx, '--', '--')
        return ('<del>%s</del>' % content, shift)


class UrlLinker(Plugin):

    def test(self, text, idx):
        if len(text[idx:]) < 10:
            return False
        else:
            return wikiMisc.isURI(text[idx:idx + 10])

    def parse(self, text, idx, acc):
        i = text[idx:].find(' ')
        if i != -1:
            i += idx + 1
        else:
            i = len(text)
        return '<a href="%s">%s</a>' % (text[idx:i].strip(), text[idx:i]), i - idx


class LinkMaker(Plugin):

    def test(self, text, idx):
        if text[idx] == '[':
            if len(text[idx:]) < 3:
                return False
            elif text[idx:idx + 2] == '[[':
                return False
            else:
                return True

    def parse(self, text, idx, page):
        # find closing tag
        pos_end = text[idx:].find(']')
        if pos_end == -1:
            return '[', 1

        link_content = text[idx + 1:pos_end + idx].strip()

        link_class = ''
        pagename = ''

        # when we have [displayed_name | addr] pattern
        if link_content.find('|') > 0:
            tmp = link_content.split('|', 1)
            link_target = tmp[1].strip()

            # we only check if the addr is URI or not.
            if wikiMisc.isURI(link_target.strip()):
                link_class = 'uri'
            else:
                page_name = link_target
                link_target = wikiSettings.site_uri + 'read/' \
                    + wikiMisc.escapeName(page_name)
                link_class = 'inside'
                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'inside_nonexist'

            link_name = tmp[0].strip()

        # otherwise, we make a link to a wiki page
        else:
            if ':' in link_content:
                tmp = link_content.split(':', 1)
                if tmp[0] in inline.mapping:
                    return inline.mapping[tmp[0]](tmp[1], acc), pos_end + 1
                else:
                    return '[%s:%s]' % (tmp[0], tmp[1]), pos_end + 1
            else:
                page_name = link_content
                link_target = '%sread/%s' \
                    % (wikiSettings.site_uri, wikiMisc.escapeName(page_name))
                link_name = link_content
                link_class = 'inside'

                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'inside_nonexist'

        if link_class == 'inside' or link_class == 'inside_nonexist':
            page.intraLinks.append(page_name)

        result = '<a href="%s" class="%s">%s</a>' % (
            link_target.strip(), link_class, link_name.strip())
        return result, pos_end + 1


class InlineLaTeX(Plugin):

    def test(self, text, idx):
        if text[idx] == '$':
            return True
        else:
            return False

    def parse(self, text, idx, acc):
        if idx != 0 and text[idx - 1] == '\\':
            return '$', idx + 2

        pos_end = text[idx + 1:].find('$')
        while text[idx + 1 + pos_end - 1] == '\\':
            pos_end = text[idx + 1 + pos_end:].find('$')
        # for incomplete syntax
        if pos_end == -1:
            return '', idx + 1
        parsed = text[idx + 1:pos_end + idx + 1].strip()
        parsed = wikiMisc.unescapeHTML(parsed.strip())
        #parsed = parsed.replace('+', '%2B')
        #parsed = parsed.replace('\n', '%0A')
        #parsed = parsed.replace(' ', '+')
        parsed = urllib.quote(parsed)
        result = '<img src="http://www.sitmo.com/gg/latex/latex2png.2.php?z=120&amp;eq=%s" alt="latex eqn" style="display:inline;" />\n' % parsed

        return result, pos_end + 2
