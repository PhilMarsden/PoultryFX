from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('pfx.urls')),
    url(r'^pfx/', include('pfx.urls')),
    url(r'^accounts/', include('pfx.urls')),
    url(r'^admin/', admin.site.urls),
]