import re

import mistune
from mistune_contrib import highlight, math

import wikiSettings


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


class Parser(object):
    def parse_markdown(self, raw_text):
        renderer = MyRenderer()
        inline = MyLexer(renderer)
        markdown = mistune.Markdown(renderer=renderer, inline=inline)

        return markdown(raw_text)
