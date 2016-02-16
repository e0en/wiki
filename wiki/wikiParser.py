from parserCommon import parse_inline, parse_inline_markdown
import wikiLinePlugins
import wikiPostProcessors
import cgi
import wikiSettings
import mistune
import re
from mistune_contrib import highlight, math

# Core functions of wikiwiki - list, header



class MyRenderer(mistune.Renderer, math.MathRendererMixin):
    def block_code(self, code, lang):
        return highlight.block_code(code, lang, True)

    def wiki_link(self, alt, link):
        return '<a href="%s">%s</a>' % (link, alt)


class MyLexer(mistune.InlineLexer, math.MathInlineMixin):
    def enable_wiki_link(self):
        self.rules.wiki_link = re.compile(
            r'\[\['
            r'([^\[^\]]+)'
            r'\]\]')
        self.default_rules.insert(0, 'wiki_link')

    def output_wiki_link(self, m):
        text = m.group(1)

        if '|' in text:
            alt, link = text.split('|')
        else:
            alt = text
            link = text

        return self.renderer.wiki_link(alt, link)


    def __init__(self, *args, **kwargs):
        super(MyLexer, self).__init__(*args, **kwargs)
        self.enable_math()
        self.enable_wiki_link()


class Parser:

    def __init__(self, settings={}):
        self.line_plugins = wikiLinePlugins.load()
        (self.pp_front, self.pp_end) = wikiPostProcessors.load()
        (self.pp_front_md, self.pp_end_md) = wikiPostProcessors.load_markdown()
        self.acc = settings
        title = self.acc['article_name']
        self.acc['site_uri'] = wikiSettings.site_uri

    # this wikiwiki parser scans the document twice.
    def parse(self, raw_text):
        raw_text = raw_text.replace('\r', '')
        raw_text = cgi.escape(raw_text)

        lines = raw_text.split('\n')

        parsed = []
        settings = {}
        p_buffer = ''

        i = 0

        # process #1. create xhtmls from text
        while 1:
            if i >= len(lines):
                break
            if lines[i].strip() == '':
                # make a paragraph
                if p_buffer.strip() != '':
                    parsed.append(
                        '<p>' + parse_inline(p_buffer.strip(), self.acc) + '</p>\n')
                    p_buffer = ''
                i += 1
            else:
                did_match = False
                for p in self.line_plugins:
                    if p.test(lines, i):
                        if p_buffer.strip() != '':
                            parsed.append('<p>' + parse_inline(p_buffer.strip(),
                                                               self.acc) + '</p>\n')
                            p_buffer = ''
                        text, offset = p.parse(lines, i, self.acc)
                        did_match = True
                        parsed.append(text)
                        i += offset
                        break

                if not did_match:
                    # accumulate current line for a paragraph
                    p_buffer += lines[i] + '\n'
                    i += 1
        # flush p_buffer if its content exists
        if p_buffer.strip() != '':
            parsed.append(
                '<p>' + parse_inline(p_buffer.strip(), self.acc) + '</p>\n')

        xhtml = ''
        for l in parsed:
            xhtml += l
        # post_processing step. it makes a list of backlink and stuffs.
        str_front = ''
        str_end = ''
        for f in self.pp_front:
            str_front += f(self.acc)
        for f in self.pp_end:
            str_end += f(self.acc)
        xhtml = str_front + xhtml + str_end

        return xhtml

    def to_markdown(self, raw_text):
        raw_text = raw_text.replace('\r', '')
        raw_text = cgi.escape(raw_text)

        lines = raw_text.split('\n')

        parsed = []
        settings = {}
        p_buffer = ''

        i = 0

        # process #1. create xhtmls from text
        while 1:
            if i >= len(lines):
                break
            if lines[i].strip() == '':
                # make a paragraph
                if p_buffer.strip() != '':
                    md = parse_inline_markdown(p_buffer.strip(), self.acc)
                    parsed.append(md + '\n\n')
                    p_buffer = ''
                i += 1
            else:
                did_match = False
                for p in self.line_plugins:
                    if p.test(lines, i):
                        if p_buffer.strip() != '':
                            md = parse_inline_markdown(
                                    p_buffer.strip(), self.acc)
                            parsed.append(md + '\n\n')
                            p_buffer = ''
                        text, offset = p.parse_markdown(lines, i, self.acc)
                        did_match = True
                        parsed.append(text)
                        i += offset
                        break

                if not did_match:
                    # accumulate current line for a paragraph
                    p_buffer += lines[i] + '\n'
                    i += 1
        # flush p_buffer if its content exists
        if p_buffer.strip() != '':
            md = parse_inline_markdown(p_buffer.strip(), self.acc)
            parsed.append(md + '\n\n')

        xhtml = ''
        for l in parsed:
            xhtml += l
        # post_processing step. it makes a list of backlink and stuffs.
        str_front = ''
        str_end = ''
        for f in self.pp_front_md:
            str_front += f(self.acc)
        for f in self.pp_end_md:
            str_end += f(self.acc)
        xhtml = str_front + xhtml + str_end

        return xhtml

    def parse_markdown(self, raw_text):
        md_text = self.to_markdown(raw_text)

        renderer = MyRenderer()
        inline = MyLexer(renderer)
        markdown = mistune.Markdown(renderer=renderer, inline=inline)

        return markdown(md_text)
