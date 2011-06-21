from django.contrib.sitemaps import Sitemap
from models import Entry, Link


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return list(Entry.live.all()) + list(Link.objects.all())

    def lastmod(self, obj):
        return obj.pub_date

    def location(self, obj):
        return obj.get_absolute_url()
