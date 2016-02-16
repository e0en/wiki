import wiki.models as wikiModels
import wiki.wikiMisc as wikiMisc


def backLinks(text, acc):
    return ''


def redirectTo(text, acc):
    if text.strip() != '':
        acc['redirect'] = text.strip()
        return '#REDIRECT [[%s]]' % acc['redirect']
    else:
        return ''
