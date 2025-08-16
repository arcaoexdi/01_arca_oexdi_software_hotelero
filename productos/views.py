from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto
from .forms import ProductoForm

# Vista para la lista de productos
def producto_list(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_list.html', {'productos': productos})

# Vista para el detalle de un producto
def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/productos_detail.html', {'producto': producto})

# Vista para el formulario de crear/editar un producto
def producto_form(request, pk=None):
    # Si existe un pk, editamos el producto correspondiente
    if pk:
        producto = get_object_or_404(Producto, pk=pk)
    else:
        producto = Producto()

    if request.method == 'POST':
        # Incluir request.FILES para manejar archivos
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        # Ajuste para BooleanField 'disponible'
        # Si no viene en POST, lo ponemos en False
        if 'disponible' not in request.POST:
            form.data = form.data.copy()
            form.data['disponible'] = False

        if form.is_valid():
            producto = form.save()
            # Respuesta AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': producto.get_absolute_url()})
            # Redirigir a la vista de detalle del producto
            return redirect('productos:producto_detail', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/productos_form.html', {'form': form, 'producto': producto})


# Vista de confirmación antes de eliminar el producto
def producto_confirm(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        # Verificar si la solicitud es AJAX para una respuesta rápida
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': '/productos/'})
        # Redirigir a la lista de productos
        return redirect('productos:producto_list')
    return render(request, 'productos/productos_confirm_delete.html', {'producto': producto})
