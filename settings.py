#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
STATIC_DOC_ROOT = os.path.join(SITE_ROOT, 'media')

MEDIA_URL = '/site_media/'


DEBUG = True
TEMPLATE_DIRS = os.path.join(SITE_ROOT, 'templates')
ROOT_URLCONF = 'urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SITE_ROOT, 'e0enwiki.db'),
    }
}
