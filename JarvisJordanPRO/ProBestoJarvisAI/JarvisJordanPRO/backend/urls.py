# facial_recognition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # otras rutas
]
