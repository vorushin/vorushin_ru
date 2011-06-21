# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse

import views
import utils

class YadisMiddleware:
  def process_request(self, request):
      if  utils.absolute_url(request.path) == utils.get_identity() and \
          'application/xrds+xml' in request.META.get('HTTP_ACCEPT', ''):
          return views.yadis(request)

  def process_response(self, request, response):
      if utils.absolute_url(request.path) == utils.get_identity():
          response['X-XRDS-Location'] = utils.absolute_url(reverse(views.yadis))
      return response
