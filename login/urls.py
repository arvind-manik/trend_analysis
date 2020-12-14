from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$',views.index,name='index'),
    url(r'create/$',views.create,name='register'),
    url(r'validate/$',views.validate,name='login'),
    url(r'graph/$',views.graph,name='graph'),
    url(r'search/$',views.search,name='search')
    ]
