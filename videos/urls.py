from django.conf.urls import patterns, url
from videos import views

urlpatterns = patterns('',
    url(r'^(?P<video_id>\d+)/$', views.detail, name='detail'),
    url(r'^get_playlist/(?P<video_id>\d+)/$', views.get_playlist, name='get_playlist'),
)
