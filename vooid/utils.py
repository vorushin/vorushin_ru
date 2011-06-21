# -*- coding:utf-8 -*-
from django.contrib.sites.models import Site
from django.conf import settings

def absolute_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    domain = Site.objects.get_current().domain
    return 'http://%s%s' % (domain, url)

def get_identity():
    return getattr(settings, 'VOOID_IDENTITY', absolute_url('/'))
