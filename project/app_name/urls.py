from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('listar/', views.listar_juegos, name='listar_juegos'),
    path('almacenar_datos/', views.almacenar, name='almacenar_datos'),
    path('buscar/', views.buscar, name='buscar'),  # Nueva ruta
    path('filtrado/', views.filtrado, name='filtrado'),  # Nueva ruta
]
