from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^yadis/$', views.yadis, name='vooid_yadis'),
    url(r'^endpoint/$', views.endpoint, name='vooid_endpoint'),
    url(r'^confirm/$', views.confirm, name='vooid_confirm'),
)
