from django.urls import path
from . import views

urlpatterns = [
    path('connect', views.connect, name='connect'),
    path('', views.index, name='index'),
]