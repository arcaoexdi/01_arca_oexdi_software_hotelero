from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ConsumoForm
from rest_framework import viewsets
from .models import Consumo, Habitacion
# consumos/views.py
from .serializers import HuespedSerializer


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
        # Usamos consistentemente "estado_habitacion" y el valor 'disponible' en minúsculas
        if not Habitacion.objects.filter(estado_habitacion='ocupada').exists():
            # Si no hay habitaciones disponibles, redirige al formulario de habitaciones
            return redirect('habitaciones:habitacion_create')
        # Si hay habitaciones disponibles, continuar con el guardado del consumo
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener habitaciones disponibles
        context['habitaciones'] = Habitacion.objects.filter(estado_habitacion='Disponible')

        # Si no hay habitaciones disponibles, agregar una variable al contexto para mostrar el mensaje
        context['no_habitaciones'] = not Habitacion.objects.filter(estado_habitacion='Disponible').exists()

        # Accede al formulario y agrega clases personalizadas a los campos
        form = context['form']
        form.fields['huesped'].widget.attrs.update({'class': 'form-control shadow-sm'})
        form.fields['producto'].widget.attrs.update({'class': 'form-control shadow-sm'})
        form.fields['cantidad'].widget.attrs.update({'class': 'form-control shadow-sm'})
        form.fields['observaciones'].widget.attrs.update({'class': 'form-control shadow-sm'})

        return context



class ConsumoUpdateView(UpdateView):
    model = Consumo
    # Eliminar 'fecha_consumo' ya que es gestionado automáticamente
    fields = ['huesped', 'producto', 'cantidad', 'observaciones']
    template_name = 'consumos/consumo_form.html'
    success_url = reverse_lazy('consumos:consumo_list')

    # Lógica adicional en caso de ser necesario al actualizar el formulario
    def form_valid(self, form):
        # Aquí puedes agregar cualquier lógica adicional antes de guardar
        return super().form_valid(form)

class ConsumoDeleteView(DeleteView):
    model = Consumo
    template_name = 'consumos/consumo_confirm_delete.html'
    success_url = reverse_lazy('consumos:consumo_list')
