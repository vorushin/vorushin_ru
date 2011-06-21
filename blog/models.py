import datetime

from django.conf import settings
from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic
from django.contrib.sitemaps import ping_google
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.text import truncate_html_words
from pingdjack.client import ping_external_urls

from blog import managers


def absolute_uri(location, request=None):
    return '%s://%s%s' % (
        'https' if request and request.is_secure() else 'http',
        Site.objects.get_current().domain,
        location)


def current_site_url():
    return absolute_uri('')


class FullAbsoluteUrlMix(object):
    def get_full_absolute_url(self):
        return absolute_uri(self.get_absolute_url())


class Tag(models.Model, FullAbsoluteUrlMix):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('blog.views.tag', args=[self.slug])


class Entry(models.Model, FullAbsoluteUrlMix):
    LIVE_STATUS = 1
    DRAFT_STATUS = 2
    HIDDEN_STATUS = 3
    STATUS_CHOICES = ((LIVE_STATUS, 'Live'),
                      (DRAFT_STATUS, 'Draft'),
                      (HIDDEN_STATUS, 'Hidden'))

    title = models.CharField(max_length=250)
    slug = models.SlugField(help_text=u'Used in the URL of the entry.')
    pub_date = models.DateTimeField(default=datetime.datetime.today)
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE_STATUS,
        help_text=u'Only entries with "Live" status will be displayed '\
                  u'publicly.')
    text_markdown = models.TextField(help_text=u'Use Markdown syntax',
                                     blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_popular = models.BooleanField(default=False)

    comments = generic.GenericRelation(
        Comment,
        content_type_field='content_type',
        object_id_field='object_pk')

    objects = models.Manager()
    live = managers.LiveEntryManager()

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Entries'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        import markdown2
        if self.text_markdown:
            self.text = markdown2.markdown(self.text_markdown)
        super(Entry, self).save(*args, **kwargs)
        if self.status == Entry.LIVE_STATUS and not settings.DEBUG:
            ping_external_urls(self.get_full_absolute_url(),
                               self.text,
                               current_site_url())
            try:
                ping_google()
            except:
                pass

    def get_absolute_url(self):
        return reverse('blog.views.entry', args=[self.id, self.slug])

    @property
    def short_text(self):
        return truncate_html_words(self.text, 50)

    @staticmethod
    def popular_entries():
        return Entry.live.filter(is_popular=True)[:10]


class Link(models.Model, FullAbsoluteUrlMix):
    title = models.CharField(max_length=250)
    url = models.URLField()
    pub_date = models.DateTimeField(default=datetime.datetime.today)
    text_markdown = models.TextField(help_text=u'Use Markdown syntax',
                                     blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    comments = generic.GenericRelation(
        Comment,
        content_type_field='content_type',
        object_id_field='object_pk')

    class Meta:
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False):
        import markdown2
        if self.text_markdown:
            self.text = markdown2.markdown(self.text_markdown)
        super(Link, self).save(force_insert, force_update)
        if not settings.DEBUG:
            ping_external_urls(self.get_full_absolute_url(),
                               '%s<br>%s' % (self.url, self.text),
                               current_site_url())
            try:
                ping_google()
            except:
                pass

    def get_absolute_url(self):
        return reverse('blog-link', args=[self.id])
