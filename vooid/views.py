# -*- coding:utf-8 -*-
from openid.server.server import Server, ProtocolError, EncodingError
try:
    from openid.extensions import sreg
except ImportError:
    from openid import sreg
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from django.utils.encoding import smart_str
from django.conf import settings

from models import TrustRoot, Store
from utils import absolute_url, get_identity

class HttpBadRequestResponse(HttpResponse):
    status_code = 400

def get_server():
    return Server(Store(), absolute_url(reverse(endpoint)))

def to_dict(d):
    return dict((k, smart_str(v)) for k, v in d.items())

def http_openid_response(server, openid_response, use_sreg=False):
    if use_sreg and hasattr(settings, 'VOOID_SREG'):
        sreg_request = sreg.SRegRequest.fromOpenIDRequest(openid_response.request)
        sreg_response = sreg.SRegResponse.extractResponse(sreg_request, settings.VOOID_SREG)
        openid_response.addExtension(sreg_response)
    try:
        webresponse = server.encodeResponse(openid_response)
    except EncodingError, e:
        return HttpBadRequestResponse(e.response.encodeToKVForm())
    response = HttpResponse(webresponse.body)
    response.status_code = webresponse.code
    for key, value in webresponse.headers.iteritems():
        response[key] = value
    return response

def _check_id(request, server, openid_request):
    identity = get_identity()
    if not request.user.is_authenticated() or \
       not request.user.is_superuser or \
       openid_request.identity != identity:
        return http_openid_response(server, openid_request.answer(False))
    if TrustRoot.objects.filter(url=openid_request.trust_root).count() > 0:
        return http_openid_response(server, openid_request.answer(True), True)
    else:
        if openid_request.immediate:
            return http_openid_response(server, openid_request.answer(False))
        request.session['check_id_request'] = openid_request
        return render_to_response('vooid/confirm.html', {
            'url': openid_request.trust_root,
        })

def yadis(request):
    return render_to_response('vooid/yadis.xml', {
        'endpoint': absolute_url(reverse(endpoint)),
        'identity': get_identity(),
    }, mimetype='application/xrds+xml')

def endpoint(request):
    server = get_server()
    try:
        openid_request = server.decodeRequest(to_dict(request.REQUEST))
    except ProtocolError, e:
        return HttpBadRequestResponse(str(e))

    if openid_request is None:
        return render_to_response('vooid/endpoint.html')

    if openid_request.mode in ('checkid_immediate', 'checkid_setup'):
        return _check_id(request, server, openid_request)
    else:
        return http_openid_response(server, server.handleRequest(openid_request))

def confirm(request):
    server = get_server()
    openid_request = request.session['check_id_request']
    if 'yes' in request.POST or 'always' in request.POST:
        if 'always' in request.POST:
            TrustRoot(url=openid_request.trust_root).save()
        return http_openid_response(server, openid_request.answer(True, identity=openid_request.identity), True)
    elif 'cancel' in request.POST:
        return http_openid_response(server, openid_request.answer(False))
    else:
        return HttpBadRequestResponse(u'Непонятное подтверждение логина')
