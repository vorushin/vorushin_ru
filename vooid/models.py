# -*- coding:utf-8 -*-
from openid.store.interface import OpenIDStore
import openid.store
from openid.association import Association as OIDAssociation
import time
import base64
import md5

from django.db import models

class TrustRoot(models.Model):
    url = models.URLField()

    def __unicode__(self):
        return self.url

# OpenID Store implementation derived mostly from Simon Willison's
# django-openid: http://code.google.com/p/django-openid/

class Nonce(models.Model):
    server_url = models.URLField(max_length=2047)
    timestamp = models.IntegerField()
    salt = models.CharField(max_length=40)

    def __unicode__(self):
        return u'%s, %s' % (self.server_url, self.salt)

class Association(models.Model):
    server_url = models.URLField(max_length=2047)
    handle = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.CharField(max_length=64)

    def __unicode__(self):
        return u'%s, %s' % (self.server_url, self.handle)

class Store(OpenIDStore):
    def storeAssociation(self, server_url, association):
        assoc = Association(
            server_url = server_url,
            handle = association.handle,
            secret = base64.encodestring(association.secret),
            issued = association.issued,
            lifetime = association.issued,
            assoc_type = association.assoc_type
        )
        assoc.save()

    def getAssociation(self, server_url, handle=None):
        assocs = Association.objects.filter(server_url=server_url)
        if handle is not None:
            assocs = assocs.filter(handle=handle)
        if not assocs:
            return None
        associations = []
        for assoc in assocs:
            association = OIDAssociation(
                assoc.handle, base64.decodestring(assoc.secret), assoc.issued,
                assoc.lifetime, assoc.assoc_type
            )
            if association.getExpiresIn() == 0:
                self.removeAssociation(server_url, assoc.handle)
            else:
                associations.append(association)
        if not associations:
            return None
        return associations[-1]

    def removeAssociation(self, server_url, handle):
        assocs = Association.objects.filter(
            server_url = server_url, handle = handle
        )
        assocs_exist = len(assocs) > 0
        assocs.delete()
        return assocs_exist

    def useNonce(self, server_url, timestamp, salt):
        # Has nonce expired?
        if abs(timestamp - time.time()) > openid.store.nonce.SKEW:
            return False
        nonce, created = Nonce.objects.get_or_create(
            server_url = server_url,
            timestamp = timestamp,
            salt = salt,
        )
        if created:
            return True
        nonce.delete()
        return False

    def cleanupNonce(self):
        Nonce.objects.filter(
            timestamp__lt = (int(time.time()) - nonce.SKEW)
        ).delete()

    def cleaupAssociations(self):
        Association.objects.extra(
            where=['issued + lifetimeint < (%s)' % time.time()]
        ).delete()

    def getAuthKey(self):
        # Use first AUTH_KEY_LEN characters of md5 hash of SECRET_KEY
        return md5.md5(settings.SECRET_KEY).hexdigest()[:self.AUTH_KEY_LEN]

    def isDumb(self):
        return False
