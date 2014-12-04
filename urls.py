from django.conf.urls.defaults import *
import wiki.views as wikiviews
import util.views as utilviews
import wiki.historyViews as wikiHistoryViews
from django.conf import settings

handler404 = 'e0en.views.my404'

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Example:
                       # (r'^e0en/', include('e0en.foo.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
                       # to INSTALLED_APPS to enable admin documentation:
                       (r'^admin/doc/',
                        include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       #(r'^admin/(.*)', admin.site.root),

                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.STATIC_DOC_ROOT}),
                       (r'^$', wikiviews.read),
                       (r'^read/(.*)', wikiviews.read),
                       (r'^test/(.*)', wikiviews.editTest),
                       (r'^googleXml/(.*)', wikiviews.googleXml),
                       (r'^edit/(.*)', wikiviews.edit),
                       (r'^jrnl/(.*)', wikiviews.readJournal),
                       (r'^delete/(.*)', wikiviews.delete),
                       (r'^process_edit/(.*)', wikiviews.processEdit),
                       (r'^recentchanges/', wikiviews.recentChanges),
                       (r'^pagelist/', wikiviews.pageList),
                       (r'^upload/', wikiviews.upload),
                       (r'^process_upload/', wikiviews.processUpload),
                       (r'^search', wikiviews.search),
                       (r'^fullhistorylist', wikiHistoryViews.fullHistoryList),
                       (r'^history_list/(.*)', wikiHistoryViews.historyList),
                       (r'^history/(.*)', wikiHistoryViews.history),
                       (r'^rollback/(.*)', wikiHistoryViews.rollback),
                       (r'^batch/', wikiviews.batch),
                       (r'^bkup/', wikiviews.bkup),
                       (r'^recover/', wikiviews.recover),
                       (r'^random/', wikiviews.random),
                       (r'^robots.txt', wikiviews.robot),
                       (r'^u/swf/(.*)', utilviews.swf),
                       )
