from wiki.views import *

def fullHistoryList(request):
    try:
        hlist = wikiModels.History.objects.filter(type__neq='new').order_by('-id')
    except:
        hlist = []
    
    return render_to_response('wiki/FullHistoryList.html', 
            {'history_list':hlist, 
                'article_name': 'All Pages', 
                'site_uri':wikiSettings.site_uri}, 
            context_instance=RequestContext(request))

def historyList(request, args):
    article_name = wikiMisc.unEscapeName(args)

    # fetch history of the page of the given name
    try:
        hlist = \
        wikiModels.History.objects.filter(name=article_name).exclude(type='new').order_by('-id')
    except:
        hlist = []

    if len(hlist) == 0:
        s = wikiSettings.site_uri + 'read/' + args.encode('utf8')
        return HttpResponseRedirect(urllib.quote(s, ':/'))
    else:
        return render_to_response('wiki/HistoryList.html', 
        {'history_list': hlist, 
            'article_name': article_name, 
            'site_uri':wikiSettings.site_uri}, 
        context_instance=RequestContext(request))


def history(request, history_id):
    #print history_id
    h = wikiModels.History.objects.get(id = history_id)
    p = Parser({'article_name':h.name})

    context = {'history_id':h.id, 'site_uri':wikiSettings.site_uri, 
    'escaped_article_name':wikiMisc.escapeName(h.name), 'article_name':h.name,
    'parsed_article_content':mark_safe(p.parse(h.content))}
    
    if 'css' in p.acc:
        context['css_additional'] = p.acc['css']

    return render_to_response('wiki/History.html', context, 
        context_instance=RequestContext(request))

def rollback(request, history_id):
    ipAddr = request.META.get('REMOTE_ADDR')
    if wikiMisc.isBlockedIP(ipAddr,wikiSettings.blocked_IPs):
        return HttpResponseRedirect(wikiSettings.site_uri)
    # fetch history of the page of the given name
    try:
        h = wikiModels.History.objects.get(id=int(history_id))
    except:
        return HttpResponseRedirect(wikiSettings.site_uri)
    
    try:
        a = wikiModels.Article.objects.get(name=h.name)
        # save current version
        h_new = wikiModels.History()
        h_new.name = a.name
        h_new.content = a.content
        h_new.ip_address = ipAddr
        h_new.save()
    
    # create new if the article is removed
    except:
        a = wikiModels.Article()
        a.name = h.name
    
    a.time_edit = datetime.now()
    a.content = h.content
    a.ip_address = ipAddr
    a.save()

    return HttpResponseRedirect(urllib.quote(wikiSettings.site_uri + 'read/' + wikiMisc.escapeName(a.name).encode('utf8'), ':/'))
