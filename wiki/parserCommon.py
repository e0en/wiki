import wikiPlugins
plugins = wikiPlugins.load()

# parse inline texts.


def parse_inline(buff, acc):
    # load inline parsing plug-ins one by one.
    idx = 0
    n = len(buff)
    result = ''
    while idx < n:
        offset = 1
        s = buff[idx]
        for p in plugins:
            if p.test(buff, idx):
                s, offset = p.parse(buff, idx, acc)
                break
        result += s
        idx += offset

    return result


def parse_inline_markdown(buff, acc):
    # load inline parsing plug-ins one by one.
    idx = 0
    n = len(buff)
    result = ''
    while idx < n:
        offset = 1
        s = buff[idx]
        for p in plugins:
            if p.test(buff, idx):
                s, offset = p.parse_markdown(buff, idx, acc)
                break
        result += s
        idx += offset

    return result


def objParseInline(buff, page):
    idx = 0
    n = len(buff)
    result = []
    while idx < n:
        offset = 1
        s = buff[idx]
        for p in objPlugins:
            if p.test(buff, idx):
                s, offset = p.parse(buff, idx, page)
                break
        result.append(s)
        idx += offset

    return result
