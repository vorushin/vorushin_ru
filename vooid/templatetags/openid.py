# -*- coding:utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

from vooid.utils import absolute_url, get_identity

register = template.Library()

@register.simple_tag
def openid_links(mode='html'):
    if mode == 'xhtml':
        ending = ' />'
    else:
        ending = '>'
    return ''.join([
        '<link rel="openid.server" href="%s"%s' % (absolute_url(reverse('vooid_endpoint')), ending),
        '<link rel="openid.delegate" href="%s"%s' % (get_identity(), ending),
    ])
