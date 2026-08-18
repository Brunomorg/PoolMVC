from django.urls import path
from . import views

urlpatterns = [
    path('', views.pool_uebersicht, name='pool_uebersicht'),
]