from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('blog.views',
    url(r'^$', 'index'),
    url(r'^archive/entries/$', 'archive_entries'),
    url(r'^archive/links/$', 'archive_links'),
    url(r'^tag/(\w+)/$', 'tag'),
    url(r'^(\d+)-([\w_-]+)/$', 'entry'),
    url(r'^link/(\d+)/$', 'link'),
    url(r'^delete_spam_comment/(\d+)/$', 'delete_spam_comment_view'),
)

urlpatterns += patterns('',
    url(r'^pingback/$', 'pingdjack.server_view', name='pingback'),
)
