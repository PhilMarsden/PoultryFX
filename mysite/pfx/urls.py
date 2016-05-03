from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^ig_view/$', views.ig_view, name='ig_view'),
    url(r'^ig_get_password/$', views.ig_view, name='ig_get_password'),
    url('^', include('django.contrib.auth.urls'))
]