from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.profile, name='profile'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^members/$', views.members, name='members'),
    url(r'^ig_positions/$', views.ig_positions, name='ig_positions'),
    url(r'^ig_activities/$', views.ig_activities, name='ig_activities'),
    url(r'^ig_trades/$', views.ig_trades, name='ig_trades'),
    url(r'^ig_get_password/$', views.ig_trades, name='ig_get_password'),
    url('^', include('django.contrib.auth.urls'))
]