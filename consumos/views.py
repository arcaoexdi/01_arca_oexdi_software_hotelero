from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ConsumoForm
from rest_framework import viewsets
from .models import Consumo, Habitacion
from .serializers import HuespedSerializer



# VISTAS DE CONSUMOS

class ConsumoCreateView(CreateView):
    model = Consumo
    form_class = ConsumoForm
    template_name = 'consumos/consumo_form.html'
    success_url = reverse_lazy('consumos:consumo_list')  # <- ¡esto es esencial!

    def form_valid(self, form):
        """
        Sobrescribimos form_valid para añadir lógica adicional cuando se crea un nuevo consumo.
        """
        # Comprobamos si existen habitaciones, de lo contrario redirigimos a crear una
        if not Habitacion.objects.exists():
            messages.warning(self.request, "No hay habitaciones registradas, por favor registra una habitación primero.")
            return redirect('habitaciones:habitacion_create')

        # Guardamos el consumo normalmente
        consumo = form.save(commit=False)

        # Validamos si producto es None
        producto = consumo.producto
        if not producto:
            form.add_error('producto', 'Este campo es obligatorio.')
            return self.form_invalid(form)

        cantidad = consumo.cantidad

        # Actualizamos el precio total del consumo según el precio del producto seleccionado
        consumo.precio_total = producto.precio_unitario * cantidad

        # Descontamos la cantidad del producto disponible
        if producto.disponible < cantidad:
            messages.error(self.request, "No hay suficiente stock para este producto.")
            return redirect('consumos:consumo_create')

        producto.disponible -= cantidad
        producto.save()

        # Finalmente, guardamos el consumo
        consumo.save()

        # Mensaje de éxito
        messages.success(self.request, "Consumo registrado correctamente.")

        # ¡Usamos el form_valid del padre para redirigir automáticamente!
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        """
        Añadimos al contexto las habitaciones disponibles para que el formulario las muestre.
        """
        context = super().get_context_data(**kwargs)
        
        # Habitaciones disponibles
        habitaciones_existentes = Habitacion.objects.all()
        context['habitaciones'] = habitaciones_existentes
        context['no_habitaciones'] = not habitaciones_existentes.exists()

        # Estilizamos el formulario
        form = context['form']
        for campo in ['habitacion', 'huesped', 'producto', 'cantidad', 'observaciones']:
            form.fields[campo].widget.attrs.update({'class': 'form-control shadow-sm'})

        return context

class ConsumoViewSet(viewsets.ModelViewSet):
    queryset = Consumo.objects.all()
    serializer_class = HuespedSerializer

class ConsumoListView(ListView):
    model = Consumo
    template_name = 'consumos/consumo_list.html'
    context_object_name = 'consumos'

class ConsumoDetailView(DetailView):
    model = Consumo
    template_name = 'consumos/consumo_detail.html'
    context_object_name = 'consumo'

def consumo_detail(request, consumo_id):
    consumo = get_object_or_404(Consumo, id=consumo_id)
    habitaciones = Habitacion.objects.all()
    context = {
        'consumo': consumo,
        'habitaciones': habitaciones,
    }
    return render(request, 'consumo/detalle.html', context)

class ConsumoUpdateView(UpdateView):
    model = Consumo
    # Solo actualizamos algunos campos, como huesped, producto, cantidad y observaciones
    fields = ['huesped', 'producto', 'cantidad', 'observaciones']
    template_name = 'consumos/consumo_form.html'
    success_url = reverse_lazy('consumos:consumo_list')

    def form_valid(self, form):
        """
        Sobrescribimos form_valid para añadir lógica adicional cuando se crea un nuevo consumo.
        """
        consumo = form.save(commit=False)
        producto = consumo.producto
        cantidad = consumo.cantidad

        # Comprobamos que el producto no sea None
        if not producto:
            form.add_error('producto', 'Este campo es obligatorio.')
            return self.form_invalid(form)

        # Calculamos el precio total
        consumo.precio_total = producto.precio_unitario * cantidad

        # Validamos si hay suficiente stock
        if producto.disponible < cantidad:
            messages.error(self.request, f"No hay suficiente stock para el producto '{producto.nombre}'.")
            return redirect('consumos:consumo_create')

        # Descontamos la cantidad del producto disponible
        producto.disponible -= cantidad
        producto.save()

        # Guardamos el consumo en la base de datos
        consumo.save()

        # Mensaje de éxito
        messages.success(self.request, f"Consumo de '{producto.nombre}' registrado correctamente.")

        # Redirigimos al detalle del consumo recién creado
        return redirect('consumos:consumo_detail', consumo_id=consumo.pk)

class ConsumoDeleteView(DeleteView):
    model = Consumo
    template_name = 'consumos/consumo_confirm_delete.html'
    success_url = reverse_lazy('consumos:consumo_list')

    def delete(self, request, *args, **kwargs):
        # Restauramos el stock del producto eliminado
        consumo = self.get_object()
        producto = consumo.producto
        producto.disponible += consumo.cantidad
        producto.save()

        # Mostramos mensaje de éxito
        messages.success(request, "Consumo eliminado y stock restaurado.")
        return super().delete(request, *args, **kwargs)


# def crear_consumo(request):
#  if request.method == 'POST':
#     form = ConsumoForm(request.POST)
#    if form.is_valid():
#       form.save()
#      return redirect('consumos:consumo_list')  # <- redirección manual
#else:
#   form = ConsumoForm()
#return render(request, 'consumos/consumo_form.html', {'form': form})