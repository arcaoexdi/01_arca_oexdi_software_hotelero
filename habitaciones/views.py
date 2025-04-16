from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from huespedes.forms import HuespedForm
from habitaciones.forms import HabitacionForm
from .models import Habitacion
from huespedes.models import Huesped
from django.db.models import Count

def some_view(request):
    habitacion = Habitacion.objects.filter(estado_habitacion="disponible")
    form = HabitacionForm()

    # Pasa las habitaciones y el formulario al template
    return render(request, 'habitacion_form.html', {'habitaciones': habitacion, 'form': form})
# --------------------------------
# 📌 Vista para listar habitaciones
# --------------------------------
class HabitacionListView(ListView):
    model = Habitacion
    template_name = 'habitaciones/habitacion_list.html'
    context_object_name = 'habitaciones'
    queryset = Habitacion.objects.annotate(num_huespedes=Count('huespedes')).order_by('numero')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total': Habitacion.objects.count(),
            'disponibles': Habitacion.objects.filter(estado_habitacion='disponible').count(),
            'ocupadas': Habitacion.objects.filter(estado_habitacion='ocupada').count(),
            'mantenimiento': Habitacion.objects.filter(estado_habitacion='mantenimiento').count(),
            
        })
        return context
    

# --------------------------------
# 📌 Vista para crear habitaciones
# --------------------------------
class HabitacionCreateView(CreateView):
    model = Habitacion
    form_class = HabitacionForm
    template_name = 'habitaciones/habitacion_form.html'
    success_url = reverse_lazy('habitaciones:habitacion_list')
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


# --------------------------------
# 📌 Vista para ver detalles de una habitación
# --------------------------------
class HabitacionDetailView(DetailView):
    model = Habitacion
    template_name = 'habitaciones/habitacion_detail.html'
    context_object_name = 'habitacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['huesped_form'] = HuespedForm()
        context['huespedes'] = self.object.huespedes.all()
        return context


# Vista para crear un huesped en la habitacion
class HabitacionUpdateView(UpdateView):
    model = Habitacion
    form_class = HabitacionForm
    template_name = 'habitaciones/habitacion_form.html'

    def get_success_url(self):
        # Redirigir al listado de habitaciones después de la actualización
        return reverse('habitaciones:habitacion_list')

    def form_valid(self, form):
        # Guardar la habitación, sin necesidad de asignar un habitacion_id
        self.object = form.save()

        # Si es una petición AJAX, devolver una respuesta con éxito y la URL de redirección
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Habitación actualizada correctamente',
                'redirect_url': reverse('habitaciones:habitacion_list')
            })

        return super().form_valid(form)

    def form_invalid(self, form):
        # Imprimir errores si el formulario es inválido
        print("❌ Formulario inválido:", form.errors)
        return super().form_invalid(form)

# --------------------------------
# 📌 Vista para eliminar habitación
# --------------------------------
class HabitacionDeleteView(DeleteView):
    model = Habitacion
    template_name = 'habitaciones/habitacion_confirm_delete.html'
    context_object_name = 'habitacion'
    success_url = reverse_lazy('habitaciones:habitacion_list')  # Redirige al listado de habitaciones

    # Método GET para mostrar la página de confirmación
    def get(self, request, *args, **kwargs):
        habitacion = self.get_object()  # Obtiene la habitación a eliminar
        return self.render_to_response({'habitacion': habitacion})

    # Método POST para eliminar la habitación
    def post(self, request, *args, **kwargs):
        habitacion = self.get_object()  # Obtiene la habitación a eliminar
        habitacion.delete()  # Elimina la habitación de la base de datos
        messages.success(request, "La habitación ha sido eliminada correctamente.")
        return redirect(self.success_url)  # Redirige al listado de habitaciones



# --------------------------------
# 📌 Crear huésped en una habitación
# --------------------------------
def crear_huesped(request, habitacion_id):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id)
    form = HuespedForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Validar si la habitación ya está llena
            if habitacion.huespedes.count() >= habitacion.capacidad:
                return render(request, 'habitacion_form.html', {
                    'form': form,
                    'habitacion': habitacion,
                    'error': '⚠️ La habitación ya alcanzó su capacidad máxima.'
                })

            huesped = form.save(commit=False)
            huesped.habitacion = habitacion
            huesped.save()

            # Si ya se completó la capacidad, marcar como ocupada
            if habitacion.huespedes.count() == habitacion.capacidad:
                habitacion.estado_habitacion = 'ocupada'
                habitacion.save()

            return redirect('huesped_list', habitacion_id=habitacion.id)

        else:
            return render(request, 'habitacion_form.html', {
                'form': form,
                'habitacion': habitacion,
                'error': '❌ El formulario contiene errores. Verifica los campos.'
            })

    # Si es GET
    return render(request, 'habitacion_form.html', {
        'form': form,
        'habitacion': habitacion
    })


# --------------------------------
# 📌 Agregar huésped a habitación
# -----------------------------
def agregar_huesped(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    num_huespedes = habitacion.huespedes.count()
    if num_huespedes >= habitacion.capacidad:
        return JsonResponse({'error': 'La habitación ya está llena.'}, status=400)
    
    form = HuespedForm(request.POST)
    if form.is_valid():
        huesped = form.save(commit=False)
        huesped.habitacion = habitacion
        huesped.save()

        if habitacion.huespedes.count() == habitacion.capacidad:
            habitacion.estado_habitacion = 'ocupada'
            habitacion.save()

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('habitaciones:huesped_list', args=[habitacion.id])
        })

    return JsonResponse({'error': 'Formulario inválido'}, status=400)

# --------------------------------
# 📌 Obtener datos de un huésped
# --------------------------------
def obtener_huesped(request, id):
    huesped = get_object_or_404(Huesped.objects.select_related('habitacion'), id=id)
    
    return JsonResponse({
        'id': huesped.id,
        'nombre': huesped.nombre,
        'apellido': huesped.apellido,
        'tipo_documento': huesped.tipo_documento,
        'numero_documento': huesped.numero_documento,
        'correo_electronico': huesped.correo_electronico,
        'telefono': huesped.telefono,
        'vehiculo': huesped.vehiculo,
        'placas': huesped.placas,
        'habitacion': huesped.habitacion.numero
    })

# --------------------------------
# 📌 Editar un huésped
# --------------------------------

def editar_huesped(request, id):
    huesped = get_object_or_404(Huesped, id=id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    nueva_habitacion_id = request.POST.get('habitacion_id')
    if nueva_habitacion_id:
        nueva_habitacion = get_object_or_404(Habitacion, pk=nueva_habitacion_id)

        if nueva_habitacion.estado_habitacion == 'ocupada' and nueva_habitacion != huesped.habitacion:
            return JsonResponse({'error': 'La habitación seleccionada ya está ocupada.'}, status=400)

        huesped.habitacion = nueva_habitacion

    for campo in ['nombre', 'apellido', 'tipo_documento', 'numero_documento', 'correo_electronico', 'telefono', 'vehiculo', 'placas']:
        valor = request.POST.get(campo)
        if valor:
            setattr(huesped, campo, valor)

    try:
        huesped.save()
        return JsonResponse({'success': True, 'redirect_url': '/huespedes/listado-completo/'})
    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error al guardar: {str(e)}'}, status=500)



# --------------------------------
# 📌 Eliminar un huésped
# --------------------------------
def eliminar_huesped(request, id):
    huesped = get_object_or_404(Huesped, id=id)
    habitacion = huesped.habitacion
    huesped.delete()

    if habitacion.huespedes.count() == 0:
        habitacion.estado_habitacion = 'disponible'
        habitacion.save()
    
    return JsonResponse({'success': True})
