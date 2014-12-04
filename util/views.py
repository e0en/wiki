import settings

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django import forms
from django.forms import widgets
from django.core.serializers import serialize, deserialize
import time
import datetime
import urllib
import os
from extnjoin import extSWFnJoinMP4


def swf(request, addr):
    extSWFnJoinMP4(
        addr, '/home/e0en/Codes/Personal/e0en/media/wiki/upload/tmp.mp4')
    url = 'http://480720.com/site_media/wiki/upload/tmp.mp4'
    return HttpResponse('<a href="%s">download here</a>' % url)
