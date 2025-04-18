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
        # Si no hay ninguna habitación en la base de datos, redirigir a crear una
        if not Habitacion.objects.exists():
            return redirect('habitaciones:habitacion_create')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Todas las habitaciones existentes, sin importar el estado
        habitaciones_existentes = Habitacion.objects.all()
        context['habitaciones'] = habitaciones_existentes
        context['no_habitaciones'] = not habitaciones_existentes.exists()

        # Estética y estilo de formulario
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
