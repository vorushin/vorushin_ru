from django.conf.urls.defaults import include, patterns, url

from blog.feeds import LatestItems, TaggedItems
from blog.sitemaps import BlogSitemap

feeds = {'entries': LatestItems,
         'tag': TaggedItems}

sitemaps = {'blog': BlogSitemap}

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'blog.views.index'),
    url(r'^blog/', include('blog.urls')),

    # comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
                              {'feed_dict': feeds}),

    # sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
                       {'sitemaps': sitemaps}),

    # very own open id server
    (r'^openid/', include('vooid.urls')),

    # admin
    (r'^admin/', include(admin.site.urls)),
)
