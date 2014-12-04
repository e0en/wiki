import wikiSettings

import wikiPlugins
from parserCommon import parse_inline
import wikiMisc
from pygments import highlight
import pygments.lexers
from pygments.formatters import HtmlFormatter
import re

import urllib
import wiki.models as wikiModels
import cgi


def load():
    plugins = [ListParser(), QuoteParser(), HeaderParser(), LaTeXParser(
    ), CodeParser(), ImageParser(), FlashParser(), RedirectTo(), BackLinks()]
    return plugins


class LinePlugin:

    def test(self, lines, idx):
        return False

    def parse(self, lines, idx, acc):
        text = ''
        offset = 1
        return text, offset

# parse Quotation syntax.
# ex: parse the syntax below:
#  ""To be or not to be, that's the question.
#  "" (Shakespeare, http://hamlet.com)
#
# to:
# <blockquote cite="http://hamlet.com">
# <p>To be or not to be, that's the question.</p>
# <cite><a href="http://hamlet.com">Shakespeare</a></cite>
# </blockquote>


class QuoteParser(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].strip()[:2] == '""'

    def parse(self, lines, idx, acc):
        n_lines = 0
        buf = ''
        src = ''
        src_uri = ''

        p = re.compile('"" +\(([^()]+)\) *$')
        n_lines = 0
        for l in lines[idx:]:
            n_lines += 1
            buf += l + '\n'
            m = p.search(l)
            if m:
                src = m.group(1)
                content = buf[2:-len(m.group(0))]
                parsed = '<blockquote>\n<p>%s</p>' % content
                parsed += '<cite>%s</cite>\n</blockquote>\n' \
                    % parse_inline(src, acc)

                return parsed, n_lines
        return buf, n_lines


class ListParser(LinePlugin):

    def isBullet(self, chr):
        return chr == '*' or chr == '#'

    def bullet2Tag(self, bullet, tag_u, tag_o):
        if bullet == '*':
            return tag_u
        elif bullet == '#':
            return tag_o
        else:
            raise

    def test(self, lines, idx):
        return self.isBullet(lines[idx].strip()[0])

    def labelDepths(self, lines):
        result = []
        for line in lines:
            j = -1
            line = line.strip()
            for i in range(0, len(line)):
                if self.isBullet(line[i]):
                    # print line[i],
                    j += 1
                if j < 0 and i >= 0 and not self.isBullet(line[i]):
                    break
                if j >= 0 and i == len(line) - 1:
                    result.append({'depth': j, 'string': line.strip() + ' '})
                    break
                elif j >= 0 and not self.isBullet(line[i]):
                    result.append({'depth': j, 'string': line.strip()})
                    break
            if j < 0:
                break

        return result

    def parseMlines(self, lines, acc):
        i = 0
        buff = ''
        while 1:
            if i < len(lines):
                line = lines[i]
            mode = ''

            depth = line['depth']

            if i > 0:
                depth_prev = lines[i - 1]['depth']
            # if current line is the first line, prepend with opening tags
            if i == 0:
                for j in range(0, len(line['string'])):
                    if self.isBullet(line['string'][j]):
                        buff += self.bullet2Tag(line['string']
                                                [j], '<ul>', '<ol>') + '<li>'
                    else:
                        break
                buff += parse_inline(line['string'][j:], acc) + '\n'
            # if current line is not a list-line, close all tags and finish
            # parsing
            elif i == len(lines):
                for j in range(depth_prev, -1, -1):
                    buff += '</li>' + \
                        self.bullet2Tag(
                            lines[i - 1]['string'][j], '</ul>', '</ol>')
                buff += '\n'
                return buff
            # if current line's bullet sequence does not match with the
            # previous line, close current tags and open new ones
            elif line['string'][0:depth_prev + 1] != lines[i - 1]['string'][0:depth_prev + 1]:
                # locate the first diffence
                diff_loc = 0
                while 1:
                    if line['string'][diff_loc] != lines[i - 1]['string'][diff_loc]:
                        break
                    else:
                        diff_loc += 1
                # add closing tags
                for j in range(depth_prev, diff_loc - 1, -1):
                    buff += '</li>' + \
                        self.bullet2Tag(
                            lines[i - 1]['string'][j], '</ul>', '</ol>')
                buff += '\n'
                # add opening tags
                if diff_loc != 0:
                    buff += '<li>'
                for j in range(diff_loc, line['depth'] + 1):
                    buff += self.bullet2Tag(line['string']
                                            [j], '<ul>', '<ol>') + '<li>'
                buff += parse_inline(line['string'][depth + 1:], acc) + '\n'
            else:
                if line['depth'] > depth_prev:
                    buff += ''
                    for j in range(depth_prev + 1, len(line['string'])):
                        if self.isBullet(line['string'][j]):
                            buff += self.bullet2Tag(line['string']
                                                    [j], '<ul>', '<ol>') + '<li>'
                        else:
                            break
                    buff += parse_inline(line['string'][j:], acc) + '\n'
                else:
                    buff += '</li><li>' + \
                        parse_inline(line['string'][depth + 1:], acc) + '\n'
            i = i + 1

    def parse(self, lines, idx, acc):
        m_lines = self.labelDepths(lines[idx:])
        return self.parseMlines(m_lines, acc), len(m_lines)


class HeaderParser(LinePlugin):

    def __init__(self):
        self.numbering = [0, 0, 0, 0, 0]

    def test(self, lines, idx):
        line = lines[idx].strip()
        if line[0] != '=':
            return False
        elif len(line) < 3:
            return False
        elif line[-1] != '=':
            return False
        else:
            return True

    def parse(self, lines, idx, page):
        line = lines[idx].strip()
        num = 0
        for i in range(0, len(line)):
            if line[i] != '=':
                num = min(5, i)
                break
        num_eq = num
        for i in range(0, num - 1):
            if self.numbering[i] == 0:
                num = i + 1
                break

        self.numbering[num - 1] += 1
        for i in range(num, 5):
            self.numbering[i] = 0

        sec_num = self.numbering[:num]
        sec_anchor = ''
        for i in range(0, num):
            sec_anchor += str(sec_num[i]) + '.'

        title = line[num_eq:-num_eq]
        for i in range(0, len(title)):
            if title[0] == title[-1] == '=':
                title = title[1:-1]
            else:
                break

        text = '<h' + str(num + 1) + ' id="sec_' + sec_anchor + '">' + \
            sec_anchor + ' ' + \
            parse_inline(title, acc) + '</h' + str(num + 1) + '>\n'

        page.chapters.append(
            {'section': sec_num, 'anchor_txt': sec_anchor, 'title': title})

        offset = 1
        return text, offset


class ImageParser(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].strip()[0:5] == '{{img'

    def parse(self, lines, idx, acc):
        i = idx
        parsed = ''
        while 1:
            if lines[i].strip()[-2:] == '}}':
                parsed += lines[i][:-2]
                break
            elif i == len(lines) - 1:
                return lines[idx], 1
            else:
                parsed += lines[i]
            i += 1
        d, l = wikiMisc.bar2Dict(parsed[6:])

        uri = l[0]

        if 'figs' not in acc:
            acc['figs'] = []

        if 'chapters' not in acc:
            section = 0
        else:
            section = acc['chapters'][-1]['section'][0]

        if len(acc['figs']) == 0:
            fig_num = 1
        elif acc['figs'][-1]['section'] == section:
            fig_num = acc['figs'][-1]['num'] + 1
        else:
            fig_num = 1

        fig_anchor = 'fig_' + str(section) + '_' + str(fig_num)
        acc['figs'].append(
            {'section': section, 'num': fig_num, 'content': parsed, 'anchor_txt': fig_anchor})

        result = '<img src="' + uri + '" '

        if 'dim' in d:
            dim = d['dim'].split('x')
            w = dim[0]
            h = dim[1]
            result += 'width="%d" height="%d" ' % (w, h)
            d.remove('dim')

        for k in d:
            result += k + '="' + d[k] + '" '

        result += '/>'
        offset = i - idx + 1

        return result, offset


class FlashParser(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].strip()[0:7] == '{{flash'

    def parse(self, lines, idx, acc):
        i = idx
        parsed = ''
        while 1:
            if lines[i].strip()[-2:] == '}}':
                parsed += lines[i][:-2]
                break
            elif i == len(lines) - 1:
                return lines[idx], 1
            else:
                parsed += lines[i]
            i += 1
        d, l = wikiMisc.bar2Dict(parsed[8:])

        uri = l[0]
        # print l

        # give a figure number
        if 'figs' not in acc:
            acc['figs'] = []

        if 'chapters' not in acc:
            section = 0
        else:
            section = acc['chapters'][-1]['section'][0]

        if len(acc['figs']) == 0:
            fig_num = 1
        elif acc['figs'][-1]['section'] == section:
            fig_num = acc['figs'][-1]['num'] + 1
        else:
            fig_num = 1

        fig_anchor = 'fig_' + str(section) + '_' + str(fig_num)
        acc['figs'].append(
            {'section': section, 'num': fig_num, 'content': parsed, 'anchor_txt': fig_anchor})
        dim = d['dim'].split('x')
        w = dim[0]
        h = dim[1]
        result = '<object width="%s" height="%s" type="application/x-shockwave-flash" data="%s"><param name="movie" value="%s" /><param name="allowFullScreen" value="true" /><param name="allowscriptaccess" value="always" /><embed src="%s" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%s" height="%s" /></object>' % (
            w, h, uri, uri, uri, w, h)

        offset = i - idx + 1

        return result, offset


class CodeParser(LinePlugin):

    def test(self, lines, idx):
        return lines[idx][0:3] == '{{{' and len(lines[idx].strip()) > 3

    def parse(self, lines, idx, acc):
        i = idx + 1
        parsed = ''
        lang = lines[idx][3:]
        while 1:
            if lines[i].strip()[-3:] == '}}}':
                parsed += lines[i][:-3]
                break
            elif i == len(lines) - 1:
                return lines[idx], 1
            else:
                parsed += lines[i] + '\n'
            i += 1

        lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(style="trac")
        code_highlighted = highlight(
            wikiMisc.unescapeHTML(parsed), lexer, formatter)

        if 'codes' not in acc:
            acc['codes'] = []

        if 'chapters' not in acc:
            section = 0
        else:
            section = acc['chapters'][-1]['section'][0]

        if len(acc['codes']) == 0:
            code_num = 1
        elif acc['codes'][-1]['section'] == section:
            code_num = acc['codes'][-1]['num'] + 1
        else:
            code_num = 1

        code_anchor = 'code_' + str(section) + '_' + str(code_num)
        acc['codes'].append(
            {'section': section, 'num': code_num, 'content': parsed, 'anchor_txt': code_anchor})

        if 'css' not in acc:
            acc['css'] = formatter.get_style_defs('#' + code_anchor)
        else:
            acc['css'] += formatter.get_style_defs('#' + code_anchor)

        result = '<div class="code" id="' + code_anchor + \
            '">\n' + code_highlighted + '</div>\n'
        offset = i - idx + 1

        return result, offset


class LaTeXParser(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].strip()[0:8] == '{{{latex'

    def parse(self, lines, idx, acc):
        i = idx + 1
        parsed = ''
        while 1:
            if lines[i].strip()[-3:] == '}}}':
                parsed += lines[i][:-3]
                break
            elif i == len(lines) - 1:
                return lines[idx], 1
            else:
                parsed += lines[i] + '\n'
            i += 1
        parsed = wikiMisc.unescapeHTML(parsed.strip())
        #parsed = parsed.replace('+', '%2B')
        #parsed = parsed.replace('\n', '%0A')
        #parsed = parsed.replace(' ', '+')
        # print parsed
        parsed = urllib.quote(parsed)

        if 'eqns' not in acc:
            acc['eqns'] = []

        if 'chapters' not in acc:
            section = 0
        else:
            section = acc['chapters'][-1]['section'][0]

        if len(acc['eqns']) == 0:
            eqn_num = 1
        elif acc['eqns'][-1]['section'] == section:
            eqn_num = acc['eqns'][-1]['num'] + 1
        else:
            eqn_num = 1

        eqn_anchor = 'eqn_' + str(section) + '_' + str(eqn_num)
        acc['eqns'].append(
            {'section': section, 'num': eqn_num, 'content': parsed, 'anchor_txt': eqn_anchor})

        result = '<div class="eqn" id="' + eqn_anchor + '"> <img src="http://www.sitmo.com/gg/latex/latex2png.2.php?z=120&amp;eq=' + parsed + '" alt="latex eqn" />\n' + \
            '<span class="eqn_id">(' + str(section) + \
            '.' + str(eqn_num) + ')</span>\n</div>\n'
        offset = i - idx + 1

        return result, offset


class RedirectTo(LinePlugin):

    def test(self, lines, idx):
        return lines[idx][0:11] == '{{redirect:' and lines[idx].find('}}') != -1

    def parse(self, lines, idx, acc):
        pos = lines[idx].find('}}')
        if pos != -1:
            parsed = lines[idx].strip()[11:pos]
            acc['redirect'] = parsed.strip()

        return 'Redirecting to <strong>%s</strong>' % acc['redirect'], 1


class TableOfContents(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].replace(' ', '').lower() == '{{tableofcontents}}'

    def parse(self, lines, idx, acc):
        return str(acc['chapters']), 1


class BackLinks(LinePlugin):

    def test(self, lines, idx):
        return lines[idx].replace(' ', '').lower().find('{{backlinks') != -1

    def parse(self, lines, idx, acc):
        p1 = lines[idx].find('backlinks')
        p2 = lines[idx].find('}}')
        s = lines[idx][p1 + 9:p2].strip()
        if s == '' or s[0] != ':':
            article_name = acc['article_name']
        else:
            article_name = s[1:].strip()

        q = article_name + ', '

        alist = wikiModels.Article.objects.filter(links__icontains=q)

        if len(alist) == 0:
            return '', 1
        else:
            buf = '<ul class="backlinks">\n'

            for a in alist:
                buf += '<li><a href="%s">%s</a></li>\n' % (
                    acc['site_uri'] + 'read/' + wikiMisc.escapeName(a.name), a.name)
            buf += '</ul>\n'
            return buf, 1
