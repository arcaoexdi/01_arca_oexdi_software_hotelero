from django.urls import path
from .views import (
    ConsumoListView,
    ConsumoDetailView,
    ConsumoCreateView,
    ConsumoUpdateView,
    ConsumoDeleteView
)

app_name = 'consumos'

urlpatterns = [
    path('', ConsumoListView.as_view(), name='consumo_list'),
    path('<int:pk>/', ConsumoDetailView.as_view(), name='consumo_detail'),
    path('nuevo/', ConsumoCreateView.as_view(), name='consumo_create'),
    path('<int:pk>/editar/', ConsumoUpdateView.as_view(), name='consumo_update'),
    path('<int:pk>/eliminar/', ConsumoDeleteView.as_view(), name='consumo_delete'),
]
