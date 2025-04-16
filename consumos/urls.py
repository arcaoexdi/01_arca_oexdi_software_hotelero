from django.urls import path, include
from .views import (
    ConsumoListView,
    ConsumoDetailView,
    ConsumoCreateView,
    ConsumoUpdateView,
    ConsumoDeleteView,
    ConsumoViewSet
)
from rest_framework.routers import DefaultRouter

app_name = 'consumos'

# Configura el router para la API
router = DefaultRouter()
router.register(r'consumos', ConsumoViewSet)

urlpatterns = [
    # Vistas de Django
    path('', ConsumoListView.as_view(), name='consumo_list'),
    path('<int:pk>/', ConsumoDetailView.as_view(), name='consumo_detail'),
    path('nuevo/', ConsumoCreateView.as_view(), name='consumo_create'),
    path('<int:pk>/editar/', ConsumoUpdateView.as_view(), name='consumo_update'),
    path('<int:pk>/eliminar/', ConsumoDeleteView.as_view(), name='consumo_delete'),
    
    # Rutas para la API REST
    path('api/', include(router.urls)),  # Rutas de la API
]
