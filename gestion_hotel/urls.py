# gestion_hotel/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/clearcache/', include('clearcache.urls')),
    path('habitaciones/', include(('habitaciones.urls', 'habitaciones'), namespace='habitaciones')),
    path('huespedes/', include(('huespedes.urls', 'huespedes'), namespace='huespedes')),
    path('consumos/', include(('consumos.urls', 'consumos'), namespace='consumos')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('', lambda request: redirect('habitaciones:habitacion_list')),
]

# Agregar esta línea para servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
