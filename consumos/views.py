from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ConsumoForm
from rest_framework import viewsets
from .models import Consumo, Habitacion
# consumos/views.py
from .serializers import HuespedSerializer



# VISTAS DE CONSUMOS


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
    context_object_name = 'consumos'



class ConsumoCreateView(CreateView):
    model = Consumo
    form_class = ConsumoForm
    template_name = 'consumos/consumo_form.html'
    success_url = reverse_lazy('consumos:consumo_list')

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

        # Actualizamos el precio total del consumo según el precio del producto seleccionado
        producto = consumo.producto
        cantidad = consumo.cantidad
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
        return redirect(self.success_url)

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
        Lógica adicional al momento de guardar la actualización de un consumo.
        """
        consumo = form.save(commit=False)
        producto = consumo.producto
        cantidad = consumo.cantidad
        precio_total = producto.precio_unitario * cantidad

        # Si la cantidad es mayor al stock, mostramos un mensaje de error
        if producto.disponible < cantidad:
            messages.error(self.request, "No hay suficiente stock para este producto.")
            return redirect('consumos:consumo_update', pk=consumo.pk)

        # Actualizamos el precio total
        consumo.precio_total = precio_total

        # Guardamos el consumo actualizado
        consumo.save()

        # Descontamos la cantidad del stock
        producto.disponible -= cantidad
        producto.save()

        messages.success(self.request, "Consumo actualizado correctamente.")
        return super().form_valid(form)


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
