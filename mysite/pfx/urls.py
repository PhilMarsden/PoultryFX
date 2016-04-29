from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'^profile/$', views.profile, name='profile'),
    url('^', include('django.contrib.auth.urls'))
]