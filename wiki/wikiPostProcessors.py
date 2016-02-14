from parserCommon import parse_inline, parse_inline_markdown


def load():
    front = []
    end = [footnote]
    return (front, end)


def load_markdown():
    front = []
    end = [footnote_markdown]
    return (front, end)


def footnote(acc):
    if 'footnote' not in acc:
        return ''
    else:
        parsed = '<ol id="footnote">\n'
        for n in xrange(len(acc['footnote'])):

            parsed += '<li id="footnote_%d">%s <a href="#rfootnote_%d">&uarr;</a></li>\n' % (
                n + 1, parse_inline(acc['footnote'][n], acc), n + 1)
        parsed += '</ol>\n'
        return parsed


def footnote_markdown(acc):
    if 'footnote' not in acc:
        return ''
    else:
        parsed = ''
        for n in xrange(len(acc['footnote'])):
            parsed += '[^%d]: %s\n' % (n + 1,
                    parse_inline_markdown(acc['footnote'][n], acc))
        return parsed
