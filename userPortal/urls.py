from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    url(r'^edit_favorites', views.edit_favorites),
    url(r'^form', views.index, name='form')
]