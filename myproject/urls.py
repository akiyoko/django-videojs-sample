from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^videos/', include('videos.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
