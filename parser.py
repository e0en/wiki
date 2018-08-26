import re

import mistune
from mistune_contrib import highlight, math


class MyRenderer(mistune.Renderer, math.MathRendererMixin):
    def block_code(self, code, lang):
        return highlight.block_code(code, lang, True)

    def wiki_link(self, alt, link):
        return f'<a href="{link}">{alt}</a>'


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


def preprocess_redirect(raw_text):
    regex = re.compile(r'#REDIRECT \[\[([^\[^\]]+)\]\]')

    match = regex.search(raw_text)
    if match:
        link = match.group(1)
        redir_str = f'Redirecting to <a href="{link}" class="redirect">{link}</a>'
        new_text = raw_text.replace(match.group(0), redir_str)
        return new_text
    else:
        return raw_text


class Parser(object):
    def parse_markdown(self, raw_text):
        renderer = MyRenderer()
        inline = MyLexer(renderer)
        markdown = mistune.Markdown(renderer=renderer, inline=inline)

        processed = preprocess_redirect(raw_text)

        return markdown(processed)
