from django.urls import path
from .views import (
    HuespedListAllView,
    HuespedDetailView,
    HuespedCreateView,
    HuespedUpdateView,
    HuespedDeleteView,
    obtener_huesped,
    eliminar_huesped,
    agregar_huesped,
    editar_huesped
)

app_name = 'huespedes'

urlpatterns = [
    # 🔹 Vistas relacionadas con habitaciones
    path('habitacion/<int:habitacion_id>/huespedes/', HuespedListAllView.as_view(), name='huesped_list'),
    path('habitacion/<int:habitacion_id>/huespedes/nuevo/', HuespedCreateView.as_view(), name='huesped_create'),

    # 🔹 Vistas de huésped individuales
    path('huesped/<int:pk>/', HuespedDetailView.as_view(), name='huesped_detail'),
    path('huesped/<int:pk>/editar/', HuespedUpdateView.as_view(), name='huesped_edit'),
    path('huesped/<int:pk>/eliminar/', HuespedDeleteView.as_view(), name='huesped_delete'),

    # 🔹 Vista de todos los huéspedes (opcional si la necesitas globalmente)
    path('listado-completo/', HuespedListAllView.as_view(), name='huesped_list_all'),

    # 🔹 Rutas AJAX
    path('ajax/huesped/<int:pk>/', obtener_huesped, name='obtener_huesped'),
    path('ajax/huesped/<int:pk>/eliminar/', eliminar_huesped, name='eliminar_huesped'),
    path('ajax/huesped/<int:habitacion_id>/agregar/', agregar_huesped, name='agregar_huesped'),
    path('ajax/huesped/<int:pk>/editar/', editar_huesped, name='editar_huesped'),
]
