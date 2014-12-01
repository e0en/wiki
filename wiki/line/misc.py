import wiki.models as wikiModels
import wiki.wikiMisc as wikiMisc

def backLinks(text, acc):
    if text.strip() == '':
        article_name = acc['article_name']
    else:
        article_name = text.strip()
    
    q = article_name + ', '

    alist = wikiModels.Article.objects.filter(links__icontains=q)
    print alist
    
    if len(alist) == 0:
        return ''
    else:
        buf = '<ul class="backlinks">\n'

        for a in alist:
            buf += '<li><a href="%s">%s</a></li>\n' % (acc['site_uri'] + 'read/' + wikiMisc.escapeName(a.name), a.name)
        buf += '</ul>\n'
        return buf

def redirectTo(text, acc):
    if text.strip() != '':
        acc['redirect'] = text.strip()
        return 'Redirecting to <strong>%s</strong>' % acc['redirect']
    else:
        return ''
        
