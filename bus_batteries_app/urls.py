from django.conf.urls import url

from . import views

app_name = 'bus_batteries_app'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add_bus/$', views.add_bus, name='add_bus', ),
]