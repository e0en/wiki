from parserCommon import parse_inline, parse_inline_markdown
import wikiLinePlugins
import wikiPostProcessors
import cgi
import wikiSettings

# Core functions of wikiwiki - list, header


class Parser:

    def __init__(self, settings={}):
        self.line_plugins = wikiLinePlugins.load()
        (self.pp_front, self.pp_end) = wikiPostProcessors.load()
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

    def parse_markdown(self, raw_text):
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
        for f in self.pp_front:
            str_front += f(self.acc)
        for f in self.pp_end:
            str_end += f(self.acc)
        xhtml = str_front + xhtml + str_end

        return "<pre>%s</pre>" % xhtml.strip()
