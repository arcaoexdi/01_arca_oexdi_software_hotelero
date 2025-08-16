from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from .forms import ConsumoForm
from .models import Consumo, Habitacion
from .serializers import HuespedSerializer

# -------------------------
# VISTAS DE CONSUMOS
# -------------------------

class ConsumoCreateView(CreateView):
    model = Consumo
    form_class = ConsumoForm
    template_name = 'consumos/consumo_form.html'
    success_url = reverse_lazy('consumos:consumo_list')

    def form_valid(self, form):
        # Verificar si hay habitaciones
        if not Habitacion.objects.exists():
            messages.warning(self.request, "No hay habitaciones registradas. Por favor crea una primero.")
            return redirect('habitaciones:habitacion_create')

        # Guardar consumo (el formulario se encarga de stock y precio)
        consumo = form.save()
        messages.success(self.request, f"Consumo de '{consumo.producto.nombre}' registrado correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habitaciones_existentes = Habitacion.objects.all()
        context['habitaciones'] = habitaciones_existentes
        context['no_habitaciones'] = not habitaciones_existentes.exists()

        # Aplicar clases CSS a los campos
        form = context['form']
        for campo in ['habitacion', 'huesped', 'producto', 'cantidad', 'observaciones']:
            form.fields[campo].widget.attrs.update({'class': 'form-control shadow-sm'})
        return context


class ConsumoUpdateView(UpdateView):
    model = Consumo
    form_class = ConsumoForm
    template_name = 'consumos/consumo_form.html'

    def form_valid(self, form):
        consumo = form.save(commit=False)
        producto = consumo.producto
        cantidad = consumo.cantidad

        original = Consumo.objects.get(pk=consumo.pk)

        # Restaurar stock anterior y descontar nueva cantidad
        producto.disponible = producto.disponible + original.cantidad - cantidad
        if producto.disponible < 0:
            messages.error(self.request, f"No hay suficiente stock para '{producto.nombre}'.")
            return self.form_invalid(form)

        producto.save()
        consumo.precio_total = consumo.total()
        consumo.save()
        messages.success(self.request, f"Consumo de '{producto.producto.nombre}' actualizado correctamente.")
        return redirect('consumos:consumo_detail', consumo_id=consumo.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habitaciones_existentes = Habitacion.objects.all()
        context['habitaciones'] = habitaciones_existentes
        context['no_habitaciones'] = not habitaciones_existentes.exists()
        return context


class ConsumoDeleteView(DeleteView):
    model = Consumo
    template_name = 'consumos/consumo_confirm_delete.html'
    success_url = reverse_lazy('consumos:consumo_list')

    def delete(self, request, *args, **kwargs):
        consumo = self.get_object()
        producto = consumo.producto
        producto.disponible += consumo.cantidad
        producto.save()
        messages.success(request, f"Consumo de '{producto.nombre}' eliminado y stock restaurado.")
        return super().delete(request, *args, **kwargs)


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
    return render(request, 'consumos/consumo_detail.html', context)


class ConsumoViewSet(viewsets.ModelViewSet):
    queryset = Consumo.objects.all()
    serializer_class = HuespedSerializer
