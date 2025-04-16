from django.urls import path
from .views import (
    HabitacionListView,
    HabitacionDetailView,
    HabitacionCreateView,
    HabitacionUpdateView,
    HabitacionDeleteView
)
from huespedes.views import (
    HuespedCreateView,
    HuespedListAllView,
    agregar_huesped,
    obtener_huesped,
    editar_huesped,
    eliminar_huesped
)

app_name = 'habitaciones'

urlpatterns = [
    # Habitaciones: listar, crear, detalle
    path('', HabitacionListView.as_view(), name='habitacion_list'),
    path('nueva/', HabitacionCreateView.as_view(), name='habitacion_create'),
    path('<int:pk>/editar/', HabitacionUpdateView.as_view(), name='habitacion_update'),
    path('<int:pk>/', HabitacionDetailView.as_view(), name='habitacion_detail'),
    
    # Eliminar para eliminar habitación
    path('<int:pk>/eliminar/', HabitacionDeleteView.as_view(), name='habitacion_confirm_delete'),

    # Huéspedes: listar todos
    path('huespedes/', HuespedListAllView.as_view(), name='huesped_list'),

    # Huéspedes por habitación
    path('habitacion/<int:habitacion_id>/huespedes/', HuespedListAllView.as_view(), name='huesped_list'),
    path('habitacion/<int:habitacion_id>/huespedes/nuevo/', HuespedCreateView.as_view(), name='huesped_create'),

    # Operaciones AJAX para huéspedes
    path('<int:pk>/agregar-huesped/', agregar_huesped, name='agregar_huesped'),
    path('huesped/<int:id>/', obtener_huesped, name='obtener_huesped'),
    path('huesped/<int:id>/editar/', editar_huesped, name='editar_huesped'),
    path('huesped/<int:id>/eliminar/', eliminar_huesped, name='eliminar_huesped'),
]
