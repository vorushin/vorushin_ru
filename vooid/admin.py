# -*- coding:utf-8 -*-
from django.contrib.admin import site, ModelAdmin

import models

site.register(models.TrustRoot)
site.register(models.Nonce)
site.register(models.Association)
