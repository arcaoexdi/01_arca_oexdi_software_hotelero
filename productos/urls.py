from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'productos'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),  # Listado de productos
    path('nuevo/', views.producto_form, name='producto_form'),  # Crear nuevo producto
    path('<int:pk>/', views.producto_detail, name='producto_detail'),  # Ver detalle de un producto
    path('<int:pk>/editar/', views.producto_form, name='producto_form'),  # Editar producto
    path('<int:pk>/confirmar_eliminacion/', views.producto_confirm, name='producto_confirm'),  # Confirmar eliminación
]

# Para servir archivos de medios en desarrollo (asegúrate de añadir esto si no está ya en tu urls.py principal)

# Si el entorno está en desarrollo (DEBUG=True), los archivos de medios se sirven desde la carpeta media/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
