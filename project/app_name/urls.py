from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('listar/', views.listar_juegos, name='listar_juegos'),
    path('almacenar_datos/', views.almacenar, name='almacenar_datos'),
    path('buscar/', views.buscar, name='buscar'),  # Nueva ruta
    path('filtrado/', views.filtrado, name='filtrado'),
    # ... (tus URLs existentes) ...
    path('cargar-recomendaciones/', views.cargar_recomendaciones, name='cargar_recomendaciones'),
    path('recomendaciones/', views.ver_recomendaciones, name='ver_recomendaciones'),
    path('recomendacionesusuarios/', views.recomendacionesusuarios, name='recomendacionesusuarios'),
]
