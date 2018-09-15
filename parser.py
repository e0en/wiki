import re

import mistune
from mistune_contrib import highlight


class MyRenderer(mistune.Renderer):
    def __init__(self, *args, **kwargs):
        mistune.Renderer.__init__(self, *args, **kwargs)
        self.wiki_links = []

    def block_code(self, code, lang):
        return highlight.block_code(code, lang, False)

    def wiki_link(self, alt, link):
        if not link.startswith('http'):
            self.wiki_links += [link]
        return f'<a class="link_inside" href="{link}">{alt}</a>'


class MyLexer(mistune.InlineLexer):
    def enable_math(self):
        regex_text = r'^[\s\S]+?(?=[\\<!\[_*`~]|https?://| {2,}\n|$|\$)'
        self.rules.text = re.compile(regex_text)
        self.rules.inline_math = re.compile(r'^\$(.*?)\$')
        self.rules.block_math = re.compile(r'^\$\$(.*?)\$\$', re.DOTALL)
        self.default_rules.insert(0, 'inline_math')
        self.default_rules.insert(0, 'block_math')

    def enable_wiki_link(self):
        self.rules.wiki_link = re.compile(
            r'\[\['
            r'([^\[^\]]+)'
            r'\]\]')
        self.default_rules.insert(0, 'wiki_link')

    def output_inline_math(self, m):
        return '$%s$' % m.group(1)

    def output_block_math(self, m):
        return '$$%s$$' % m.group(1)

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
        redir_str = (f'Redirecting to <a href="{link}" class="redirect">'
                     f'{link}</a>')
        new_text = raw_text.replace(match.group(0), redir_str)
        return new_text
    else:
        return raw_text


class Parser(object):
    def __init__(self):
        self.renderer = MyRenderer()

    def gen_backlink_html(self, backlinks):
        if backlinks:
            result = ['<h2>Backlinks</h2>']
            result += ['<ul class="backlinks">']
            for l in backlinks:
                result += [f'<li><a class="link_inside" '
                           f'href="{l}">{l}</a></li>']
            result += ['</ul>']
            return '\n'.join(result)
        else:
            return ''

    def parse_markdown(self, raw_text):
        inline = MyLexer(self.renderer)
        markdown = mistune.Markdown(renderer=self.renderer, inline=inline)

        processed = preprocess_redirect(raw_text)
        return markdown(processed)

    @property
    def wiki_links(self):
        return self.renderer.wiki_links
