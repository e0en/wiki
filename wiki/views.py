import settings
import wikiSettings

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.template import RequestContext
import models as wikiModels
from django.utils.safestring import mark_safe
from django import forms
from django.forms import widgets
from django.core.serializers import serialize, deserialize
from wikiParser import Parser
import wikiMisc
import time
import datetime
import urllib
from datetime import datetime
import os
from ftplib import FTP
import PyRSS2Gen


def robot(request):
    robot_txt = 'User-agent: *\nDisallow: /'
    return HttpResponse(robot_txt)


def batch_markdown(request):
    articles = wikiModels.Article.objects.all()

    for a in articles:
        p = Parser({'article_name': a.name})
        a.markdown = p.to_markdown(a.content)
        a.save()


    return HttpResponse('Conversion to Markdown is complete')


def bkup(request):
    model_names = ['Author', 'Article', 'Media', 'History', 'Settings']
    for model_name in model_names:
        cls = getattr(wikiModels, model_name)
        filename = '%s.json' % model_name.lower()
        f = open(os.path.join(settings.SITE_ROOT, filename), 'w')
        f.write(serialize('json', cls.objects.all()))
        f.close()
    return HttpResponse('Backup done in %s' % settings.SITE_ROOT)


def recover(request):
    model_names = ['Author', 'Article', 'Media', 'History', 'Settings']
    for model_name in model_names:
        filename = '%s.json' % model_name.lower()
        f = open(os.path.join(settings.SITE_ROOT, filename), 'r')
        json = f.read()
        data = deserialize('json', json)
        for d in data:
            print 'saving %s' % d
            d.save()

    return HttpResponse('Full recovery is done from backup data in %s' % settings.SITE_ROOT)


def random(request, args=''):
    a = wikiModels.Article.objects.order_by('?')[0]
    return HttpResponseRedirect(wikiSettings.site_uri + 'read/' + a.name)


def read(request, args=''):
    t_start = time.time()
    # in case of null article name, go to main page
    if args.strip() == '':
        return HttpResponseRedirect(wikiSettings.site_uri + 'read/' +
                                    wikiSettings.main_page)
    article_name = wikiMisc.unEscapeName(args)

    # in case of nonexisting article, go to search page
    try:
        a = wikiModels.Article.objects.get(name=article_name)
    except wikiModels.Article.DoesNotExist:
        return HttpResponseRedirect(urllib.quote((wikiSettings.site_uri +
                                                  'search?q=' + article_name).encode('utf8'), '?=/:'))

    a_prev = wikiModels.Article.objects.filter(
        name__lt=a.name).order_by('-name')
    a_next = wikiModels.Article.objects.filter(
        name__gt=a.name).order_by('name')
    prev_page = None
    next_page = None
    if a_prev:
        prev_page = a_prev[0]
    if a_next:
        next_page = a_next[0]
    # parse the page
    p = Parser({'article_name': article_name})
    #op = ObjParser(article_name)
    content = p.parse(a.content)
    #o_content = op.parse(a.content)

    context = {'site_uri': wikiSettings.site_uri,
               'escaped_article_name': wikiMisc.escapeName(a.name),
               'article_name': a.name,
               'parsed_article_content': mark_safe(content),
               'generate_time': round(time.time() - t_start, 6),
               'prev_page': prev_page,
               'next_page': next_page,
               }
    if 'q' in request.GET:
        context['search_query'] = request.GET['q']
    if 'css' in p.acc:
        context['css_additional'] = p.acc['css']
    if 'redirect' in p.acc:
        context['redirect'] = p.acc['redirect']

    wikiMisc.addLog(wikiSettings.log_filename,
                    request.META.get('REMOTE_ADDR'), 'Read', a.name)

    return render_to_response('wiki/Read.html', context,
                              context_instance=RequestContext(request))


def markdown(request, args=''):
    t_start = time.time()
    # in case of null article name, go to main page
    if args.strip() == '':
        return HttpResponseRedirect(wikiSettings.site_uri + 'markdown/' +
                                    wikiSettings.main_page)
    article_name = wikiMisc.unEscapeName(args)

    # in case of nonexisting article, go to search page
    try:
        a = wikiModels.Article.objects.get(name=article_name)
    except wikiModels.Article.DoesNotExist:
        return HttpResponseRedirect(urllib.quote((wikiSettings.site_uri +
                                                  'search?q=' + article_name).encode('utf8'), '?=/:'))

    a_prev = wikiModels.Article.objects.filter(
        name__lt=a.name).order_by('-name')
    a_next = wikiModels.Article.objects.filter(
        name__gt=a.name).order_by('name')
    prev_page = None
    next_page = None
    if a_prev:
        prev_page = a_prev[0]
    if a_next:
        next_page = a_next[0]

    # parse the page
    p = Parser({'article_name': article_name})
    content = p.parse_markdown(a.content)

    context = {'site_uri': wikiSettings.site_uri,
               'escaped_article_name': wikiMisc.escapeName(a.name),
               'article_name': a.name,
               'parsed_article_content': mark_safe(content),
               'generate_time': round(time.time() - t_start, 6),
               'prev_page': prev_page,
               'next_page': next_page,
               }
    if 'q' in request.GET:
        context['search_query'] = request.GET['q']
    if 'css' in p.acc:
        context['css_additional'] = p.acc['css']
    if 'redirect' in p.acc:
        context['redirect'] = p.acc['redirect']

    wikiMisc.addLog(wikiSettings.log_filename,
                    request.META.get('REMOTE_ADDR'), 'Markdown', a.name)

    return render_to_response('wiki/Read.html', context,
                              context_instance=RequestContext(request))


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Test Code

def editTest(request, args=''):
    if args.strip() == '':
        return HttpResponseRedirect('../')
    article_name = wikiMisc.unEscapeName(args)
    try:
        a = wikiModels.Article.objects.get(name=article_name)
    except wikiModels.Article.DoesNotExist:
        a = wikiModels.Article()
        a.name = article_name
        a.content = ''

    context = {'site_uri': wikiSettings.site_uri,
               'escaped_article_name': args,
               'article_name': article_name,
               'article_content': a.content}

    return render_to_response('wiki/EditTest.html', context,
                              context_instance=RequestContext(request))

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<Test Code


def edit(request, args):
    if args.strip() == '':
        return HttpResponseRedirect('../')
    article_name = wikiMisc.unEscapeName(args)
    try:
        a = wikiModels.Article.objects.get(name=article_name)
    except wikiModels.Article.DoesNotExist:
        a = wikiModels.Article()
        a.name = article_name
        a.content = ''
    #suggestion = wikiMisc.spellCorrection(article_name)
    suggestion = None

    context = {'site_uri': wikiSettings.site_uri,
               'escaped_article_name': args,
               'article_name': article_name,
               'article_content': a.content}
    if suggestion != None:
        context['suggestion'] = suggestion
    return render_to_response('wiki/Edit.html', context,
                              context_instance=RequestContext(request))


def readJournal(request, args):
    d = datetime.now()
    date = '%d-%02d-%02d' % (d.year, d.month, d.day)
    return HttpResponseRedirect(wikiSettings.site_uri + 'read/%s' % date)


def delete(request, args):
    ip_addr = request.META.get('REMOTE_ADDR')
    if wikiMisc.isBlockedIP(ip_addr, wikiSettings.blocked_IPs):
        return HttpResponseRedirect(urllib.quote(wikiSettings.site_uri, ':/'))

    if args.strip() == '':
        return HttpResponseRedirect('../')
    article_name = wikiMisc.unEscapeName(args)
    try:
        a = wikiModels.Article.objects.get(name=article_name)
    except wikiModels.Article.DoesNotExist:
        return HttpResponseRedirect(wikiSettings.site_uri + 'read/')

    # create a new history entry
    h = wikiModels.History()
    h.name = a.name
    h.content = a.content
    h.type = 'del'
    h.ip_address = request.META.get('REMOTE_ADDR')
    h.save()

    a.delete()

    wikiMisc.addLog(wikiSettings.log_filename,
                    request.META.get('REMOTE_ADDR'), 'Delete', article_name)

    return HttpResponseRedirect(wikiSettings.site_uri + 'read/')


def recentChanges(request):
    histlist = wikiModels.History.objects.order_by('-time')
    hlist = []
    d_current = ''
    names_in_day = []
    titlelist = []
    for item in histlist:
        h = {}
        day = item.time.strftime('%Y.%m.%d')
        h['name'] = item.name
        h['name_esc'] = wikiMisc.escapeName(item.name)
        h['time_edit'] = item.time.strftime('%H:%M:%S')
        h['ip_address'] = item.ip_address
        h['type'] = item.type
        if item.name in titlelist:
            continue
        else:
            titlelist.append(item.name)
        if d_current == '':
            d_current = item.time.strftime('%Y.%m.%d')
            tmp = {'date': d_current, 'changes': [h]}
            names_in_day.append(item.name + ',' + item.type)
        elif d_current != day:
            hlist.append(tmp)
            tmp = {'date': day, 'changes': [h]}
            names_in_day.append(item.name + ',' + item.type)
            d_current = day
        elif item.name + ',' + item.type not in names_in_day:
            tmp['changes'].append(h)
            names_in_day.append(item.name + ',' + item.type)
    hlist.append(tmp)
    return render_to_response('wiki/RecentChanges.html',
                              {'history_list': hlist,
                                  'site_uri': wikiSettings.site_uri},
                              context_instance=RequestContext(request))


def pageList(request):
    alist = wikiModels.Article.objects.order_by('name')

    # code to sort page names using python's sort function.
    # to be replaced by postgreSQL's sort functionality when
    # I figure out how to properly sort page names using postgreSQL

    article_list = []
    for a in alist:
        article_list.append(
            {'uri': wikiMisc.escapeHTML(a.name), 'name': a.name})
    # article_list.sort()

    context = {'article_list': article_list, 'site_uri': wikiSettings.site_uri}
    return render_to_response('wiki/PageList.html', context,
                              context_instance=RequestContext(request))


def upload(request):
    file_names = os.listdir(wikiSettings.upload_path)
    return render_to_response('wiki/Upload.html',
                              {'form': 'f', 'site_uri': wikiSettings.site_uri,
                                  'file_names': file_names},
                              context_instance=RequestContext(request))


def processUpload(request):
    if request.method == 'POST':
        f = request.FILES['file']
        filename = str(f)
        f_server = open(
            os.path.join(wikiSettings.upload_path, filename), 'wb+')
        for chunk in f.chunks():
            f_server.write(chunk)
        f_server.close()
        return HttpResponseRedirect(wikiSettings.site_uri + 'upload/')
    return HttpResponseRedirect(wikiSettings.site_uri)


def processEdit(request, args):
    ip_addr = request.META.get('REMOTE_ADDR')
    if wikiMisc.isBlockedIP(ip_addr, wikiSettings.blocked_IPs):
        # print urllib.quote(wikiSettings.site_uri, ':/')
        return HttpResponseRedirect(urllib.quote(wikiSettings.site_uri, ':/'))

    content = request.POST['content']
    article_name = wikiMisc.unEscapeName(args)

    if not wikiMisc.isArticleName(article_name):
        return HttpResponseRedirect(wikiSettings.site_uri)

    # initiate parser
    p = Parser({'article_name': article_name})

    # create or edit the article
    try:
        a = wikiModels.Article.objects.get(name=article_name)

        # skip editing process if the page is unchanged
        if a.content == content:
            s = (wikiSettings.site_uri + 'read/' +
                 wikiMisc.escapeName(a.name)).encode('utf8')
            return HttpResponseRedirect(urllib.quote(s, ':/'))

        # otherwise, save current version as a new history entry
        else:
            # create a new history entry
            h = wikiModels.History()
            h.name = a.name
            h.content = a.content
            h.ip_address = request.META.get('REMOTE_ADDR')
            h.save()

    except wikiModels.Article.DoesNotExist:
        a = wikiModels.Article()
        a.name = article_name

        # create a new history entry
        h = wikiModels.History()
        h.name = a.name
        h.content = a.content
        h.type = 'new'
        h.ip_address = request.META.get('REMOTE_ADDR')
        h.save()

    a.ip_address = request.META.get('REMOTE_ADDR')
    a.time_edit = datetime.now()
    a.content = content
    a.content_html = p.parse(content)

    if 'links' in p.acc:
        links = ''
        for l in p.acc['links']:
            links += l + ', '
            a.links = links
    a.save()

    wikiMisc.addLog(wikiSettings.log_filename, request.META.get(
        'REMOTE_ADDR'), 'Edit', article_name)

    s = wikiSettings.site_uri + 'read/' + \
        wikiMisc.escapeName(a.name).encode('utf8')

    return HttpResponseRedirect(urllib.quote(s, ':/'))


def search(request):
    # do not allow bots to search this wikiwiki
    ip_addr = request.META.get('REMOTE_ADDR')
    if wikiMisc.isBlockedIP(ip_addr, wikiSettings.blocked_IPs):
        # print urllib.quote(wikiSettings.site_uri, ':/')
        return HttpResponseRedirect(urllib.quote(wikiSettings.site_uri, ':/'))

    q = ''
    if request.method == 'GET':
        q = request.GET['q'].strip()
    alist = wikiModels.Article.objects.filter(name__icontains=q)
    match_list = []
    exact_match = None

    if len(alist) > 0:
        for a in alist:
            if q.lower() == a.name.lower():
                exact_match = a.name
            else:
                match_list.append(a.name)

    #suggestion = wikiMisc.spellCorrection(q)
    suggestion = None

    '''
    if exact_match != None:
        uri = urllib.quote(wikiSettings.site_uri +
            'read/' + wikiMisc.escapeName(exact_match).encode('utf8'), ':/')
        if m != q:
            uri += '?q=' + wikiMisc.escapeName(q).encode('utf8')
        return HttpResponseRedirect(uri)
    '''

    alist_fulltext = wikiModels.Article.objects.filter(content__icontains=q)
    fullmatch_list = []

    if len(alist_fulltext) > 0:
        for a in alist_fulltext:
            fullmatch_list.append(a.name)

    context = {'match_list': match_list,
               'fullmatch_list': fullmatch_list,
               'exact_match': exact_match,
               'query': q,
               'site_uri': wikiSettings.site_uri}
    if suggestion != None:
        context['suggestion'] = suggestion
    return render_to_response('wiki/Search.html', context, context_instance=RequestContext(request))


def rss(request):
    alist = wikiModels.Article.objects.order_by('-time_edit')

    # code to sort page names using python's sort function.
    # to be replaced by postgreSQL's sort functionality when
    # I figure out how to properly sort page names using postgreSQL

    rss = PyRSS2Gen.RSS2(title='e0enWiki', link='http://480720.com/wiki',
                         description='Recently changed/created documents of e0enWiki',
                         lastBuildDate=datetime.datetime.now(), items='')
    for a in alist:
        item = PyRSSGen.RSSItem(
            title=a.name, link='http://480720.com/wiki/read/%s' % a.name,
            description=a.content, pubdate=a.time_edit,
            guid='http://480720.com/wiki/read/%s' % a.name)

    context = {'article_list': article_list, 'site_uri': wikiSettings.site_uri}
    return render_to_response('wiki/PageList.html', context,
                              context_instance=RequestContext(request))


def googleXml(request, args):
    return HttpResponse("NotImplemented")


def rename(request, args):
    pass
    # rename current page
    # find all links pointing to current page, and rename them

# this will be modified on my instant needs


def batch(request):
    pass
