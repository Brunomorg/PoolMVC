from django.urls import path
from . import views

urlpatterns = [
    path('', views.themen_liste, name='themen_liste'),
    path('thema/<int:thema_id>/', views.thema_detail, name='thema_detail'),
path('ausgabe/<int:ausgabe_id>/bearbeiten/', views.ausgabe_bearbeiten, name='ausgabe_bearbeiten'),
]