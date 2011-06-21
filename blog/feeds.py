# -*- coding: utf-8 -*-
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed

from blog.models import Entry, Link, Tag


class MyFeed(Feed):
    feed_type = Atom1Feed
    author_name = u'Роман Ворушин'
    author_email = 'roman.vorushin@gmail.com'
    author_link = 'http://vorushin.ru/'


class LatestItems(MyFeed):
    title = u'Блог Романа Ворушина'
    link = '/blog/'
    subtitle = u'Свежие записи и интересные ссылки из блога Романа Ворушина'
    title_template = 'blog/feeds/title.html'
    description_template = 'blog/feeds/description.html'

    def items(self, obj):
        objects = list(Entry.live.all()[:5]) + list(Link.objects.all()[:5])
        return sorted(objects, key=lambda obj: -obj.pub_date)


class TaggedItems(Feed):
    title_template = 'blog/feeds/title.html'
    description_template = 'blog/feeds/description.html'

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(slug=bits[0])

    def title(self, obj):
        return u'Блог Романа Ворушина, категория "%s"' % obj.title

    def description(self, obj):
        return u'Свежие записи и интересные ссылки из категории "%s" блога ' \
               u'Романа Ворушина' % obj.title

    def items(self, obj):
        objects = list(Entry.live.filter(tags__in=[obj])[:5]) + \
                  list(Link.objects.filter(tags__in=[obj])[:5])
        return sorted(objects, key=lambda obj: -obj.pub_date)
