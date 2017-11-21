from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^imagens/$', views.imagens, name='imagens'),
    url(r'^cruzar/$', views.cruzar, name='cruzar'),
    url(r'^receber_ignoradas/$', views.receber_ignoradas, name='receber_ignoradas'),
    url(r'^is_cruzando/$', views.is_cruzando, name='is_cruzando'),
    url(r'^get_geradas/$', views.get_geradas, name='get_geradas'),
    url(r'^nova_sessao/$', views.nova_sessao, name='nova_sessao'),
]