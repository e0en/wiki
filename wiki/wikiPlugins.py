import wikiSettings
import wikiMisc
import re
import models as wikiModels
import inline
import latex


def load():
    plugins = []

    # order DOES matter.
    plugins = [CarrageReturn(), SpecialChar(), InlineCode(), Strike(),
               FootNote(), LinkMaker(), InlineLaTeX(
    ), UrlLinker(), Emphasize(),
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

    def parse(self, text, idx, acc):
        return text[idx], 1

    def parse_markdown(self, text, idx, acc):
        return self.parse(text, idx, acc)


class CarrageReturn(Plugin):

    def test(self, text, idx):
        return text[idx] == '\n'

    def parse(self, text, idx, acc):
        return '<br />\n', 1

    def parse_markdown(self, text, idx, acc):
        return '\n', 1


class SpecialChar(Plugin):

    def test(self, text, idx):
        if text[idx] == '\\':
            return True
        else:
            return False

    def parse(self, text, idx, acc):
        special_chars = ['$', '[', ']', '\\']
        if text[idx + 1] in special_chars:
            return text[idx + 1], 2
        else:
            return '\\', 1


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
            parsed = '<q><a href="%s">%s</a></q>' % (self.src, self.content)
        else:
            parsed = '<q title="%s">%s</q>' % (self.src, self.content)
        return parsed, self.length


class InlineCode(Plugin):

    def test(self, text, idx):
        return findTag(text, idx, '[[code:', ']]')

    def parse(self, text, idx, acc):
        (content, shift) = extractContent(text, idx, '[[code:', ']]')
        return ('<code>' + content + '</code>', shift)
    
    def parse_markdown(self, text, idx, acc):
        (content, shift) = extractContent(text, idx, '[[code:', ']]')
        return ('`' + content + '`', shift)


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

    def parse_markdown(self, text, idx, acc):
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
                return '*' + txt + '*', idx_end - idx
            elif n_mark == 3:
                return '**' + txt + '**', idx_end - idx
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
        m = re.search(r'[ \n\r]', text[idx:])

        if m != None:
            i = m.start() + idx + 1
        else:
            i = len(text)
        return '<a href="%s" class="link_external">%s</a>' % (text[idx:i].strip(), text[idx:i]), i - idx

    def parse_markdown(self, text, idx, acc):
        m = re.search(r'[ \n\r]', text[idx:])

        if m != None:
            i = m.start() + idx + 1
        else:
            i = len(text)
        return text[idx:i].strip() + ' ', i - idx


class FootNote(Plugin):

    def test(self, text, idx):
        if text[idx:idx + 2] == '[*':
            if len(text[idx:]) < 3:
                return False
            else:
                return True

    def parse(self, text, idx, acc):
        # find closing tag
        pos_end = text[idx:].find(']')
        if pos_end == -1:
            return '[*', 2

        content = text[idx + 2:pos_end + idx].strip()
        if 'footnote' not in acc:
            acc['footnote'] = [content]
        else:
            acc['footnote'].append(content)
        n = len(acc['footnote'])
        link_addr = '#footnote_%d' % n
        parsed = '<a id="rfootnote_%d" href="%s" title="%s" />[%d]</a>' % (
            n, link_addr, content, n)
        return parsed, pos_end + 1

    def parse_markdown(self, text, idx, acc):
        pos_end = text[idx:].find(']')
        if pos_end == -1:
            return '[*', 2

        content = text[idx + 2:pos_end + idx].strip()
        if 'footnote' not in acc:
            acc['footnote'] = [content]
        else:
            acc['footnote'].append(content)
        n = len(acc['footnote'])
        link_addr = '#footnote_%d' % n

        parsed = '[^%d]' % n
        return parsed, pos_end + 1


class LinkMaker(Plugin):

    def test(self, text, idx):
        if text[idx] == '[':
            if len(text[idx:]) < 3:
                return False
            elif text[idx:idx + 2] == '[[':
                return False
            else:
                return True

    def parse(self, text, idx, acc):
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
                link_class = 'link_external'
            else:
                page_name = link_target
                link_target = wikiSettings.site_uri + 'read/' \
                    + wikiMisc.escapeName(page_name)
                link_class = 'link_inside'
                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'link_inside_nonexist'

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
                link_class = 'link_inside'

                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'link_inside_nonexist'

        if link_class == 'link_inside' or link_class == 'link_inside_nonexist':
            if 'links' not in acc:
                acc['links'] = []
            acc['links'].append(page_name)

        result = '<a href="%s" class="%s">%s</a>' % (
            link_target.strip(), link_class, link_name.strip())
        return result, pos_end + 1

    def parse_markdown(self, text, idx, acc):
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
            link_name = tmp[0].strip()
            link_target = tmp[1].strip()

            # we only check if the addr is URI or not.
            if wikiMisc.isURI(link_target.strip()):
                result = '[%s](%s)' % (link_name, link_target)
                return result, pos_end + 1

            else:
                page_name = link_target
                link_class = 'link_inside'
                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'link_inside_nonexist'


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
                link_name = link_content.strip()
                link_target = link_content.strip()

                try:
                    a = wikiModels.Article.objects.get(name=page_name)
                except wikiModels.Article.DoesNotExist:
                    link_class = 'link_inside_nonexist'

        if link_class == 'link_inside' or link_class == 'link_inside_nonexist':
            if 'links' not in acc:
                acc['links'] = []
            acc['links'].append(page_name)

        if link_name == link_target:
            result = '[[%s]]' % link_name
        else:
            result = '[[%s|%s]]' % (link_name, link_target)
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

        result = '\\(%s\\)' % latex.preprocess(parsed)
        return result, pos_end + 2

    def parse_markdown(self, text, idx, acc):
        if idx != 0 and text[idx - 1] == '\\':
            return '$', idx + 2

        pos_end = text[idx + 1:].find('$')
        while text[idx + 1 + pos_end - 1] == '\\':
            pos_end = text[idx + 1 + pos_end:].find('$')
        # for incomplete syntax
        if pos_end == -1:
            return '', idx + 1
        parsed = text[idx + 1:pos_end + idx + 1].strip()

        result = '$%s$' % latex.preprocess(parsed)
        return result, pos_end + 2


