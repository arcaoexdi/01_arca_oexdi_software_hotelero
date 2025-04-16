import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt

from habitaciones.models import Habitacion
from .models import Huesped
from .forms import HuespedForm

logger = logging.getLogger(__name__)


# =========================
# ✅ LISTAR TODOS LOS HUÉSPEDES (sin filtrar por habitación)
# =========================
class HuespedListAllView(ListView):
    model = Huesped
    template_name = 'huespedes/huespedes_list.html'
    context_object_name = 'huespedes'

    def get_queryset(self):
        habitacion_id = self.kwargs.get('habitacion_id')
        queryset = Huesped.objects.all().select_related('habitacion')
        return queryset.filter(habitacion_id=habitacion_id) if habitacion_id else queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habitacion_id = self.kwargs.get('habitacion_id')
        if habitacion_id:
            context['habitacion'] = Habitacion.objects.get(pk=habitacion_id)
        return context


# =========================
# ✅ CREAR UN HUÉSPED Y ASIGNARLO A UNA HABITACIÓN
# =========================
class HuespedCreateView(CreateView):
    model = Huesped
    form_class = HuespedForm
    template_name = 'huespedes/huespedes_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['habitacion'] = get_object_or_404(Habitacion, pk=self.kwargs.get('habitacion_id'))
        return context

    def form_valid(self, form):
        habitacion = get_object_or_404(Habitacion, pk=self.kwargs["habitacion_id"])
        huesped = form.save(commit=False)
        huesped.habitacion = habitacion

        # ✅ Verificamos si la habitación está llena usando la propiedad capacidad_actual
        if habitacion.capacidad_actual >= habitacion.capacidad:
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "La habitación ya ha alcanzado su capacidad máxima."})
            form.add_error(None, "La habitación ya ha alcanzado su capacidad máxima.")
            return self.form_invalid(form)

        # ✅ Guardamos huésped (no actualizamos capacidad_actual manualmente porque es una propiedad)
        huesped.save()

        # ⚡ Si es petición AJAX, devolvemos JSON con redirect_url
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            url = reverse("habitaciones:huesped_list", kwargs={"habitacion_id": habitacion.id})
            return JsonResponse({"success": True, "redirect_url": url})

        # 🔁 Si no es AJAX, redireccionamos normalmente
        return redirect("habitaciones:huesped_list", habitacion_id=habitacion.id)

    def get_success_url(self):
        return reverse('habitaciones:huesped_list', kwargs={'habitacion_id': self.kwargs.get('habitacion_id')})

    def get_initial(self):
        initial = super().get_initial()
        habitacion_id = self.kwargs.get("habitacion_id")
        if habitacion_id:
            initial["habitacion"] = get_object_or_404(Habitacion, pk=habitacion_id)
        return initial



# =========================
# ✅ DETALLE DE UN HUÉSPED
# =========================
class HuespedDetailView(DetailView):
    model = Huesped
    template_name = 'huespedes/huespedes_detail.html'


# =========================
# ✅ EDITAR UN HUÉSPED
# =========================
# =========================
class HuespedUpdateView(UpdateView):
    model = Huesped
    form_class = HuespedForm
    template_name = 'huespedes/huespedes_form.html'

    def form_valid(self, form):
        # Guardar el objeto Huesped pero sin confirmarlo aún
        self.object = form.save(commit=False)

        # Agregar logs para verificar los valores
        logger.debug(f"Guardando huésped: {self.object}")

        # Obtener habitacion_id desde la URL
        habitacion_id = self.request.GET.get('habitacion_id')
        logger.debug(f"habitacion_id desde la URL: {habitacion_id}")
        
        # Verificar si existe habitacion_id en la URL
        if habitacion_id:
            habitacion = Habitacion.objects.filter(pk=habitacion_id).first()
            if habitacion:
                # Asignar la habitación al huésped
                self.object.habitacion = habitacion
            else:
                # Si no se encuentra la habitación, se registra un error
                logger.error(f"Habitación no encontrada con ID: {habitacion_id}")
                form.add_error(None, 'Habitación no encontrada')
                return self.form_invalid(form)

        # Guardar el objeto huésped
        self.object.save()

        # Si la petición es AJAX, retornar una respuesta JSON
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Huésped actualizado correctamente"})

        # Si no es AJAX, redirigir a la página de éxito
        return super().form_valid(form)

    def get_success_url(self):
        # Si el huésped tiene habitación, redirigir a la lista de huéspedes de esa habitación
        habitacion_id = getattr(self.object.habitacion, 'id', None)
        if habitacion_id:
            return reverse('huespedes:huesped_list', kwargs={'habitacion_id': habitacion_id})

        # Si no tiene habitación asignada, lanzar error 404
        raise Http404("El huésped no tiene una habitación asignada")




# =========================
# ✅ ELIMINAR UN HUÉSPED
# =========================
class HuespedDeleteView(DeleteView):
    model = Huesped
    template_name = 'huespedes/huespedes_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        habitacion = self.object.habitacion
        habitacion_id = habitacion.id

        self.object.delete()

        if habitacion.huespedes.count() < habitacion.capacidad:
            habitacion.disponible = True
            habitacion.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "message": "Huésped eliminado correctamente"})

        return HttpResponseRedirect(reverse('huespedes:huesped_list', kwargs={'habitacion_id': habitacion_id}))

    def get_success_url(self):
        return reverse('huespedes:huesped_list_all')


# =========================
# 🚀 VISTAS AJAX
# =========================
@csrf_exempt
def obtener_huesped(request, pk):
    huesped = get_object_or_404(Huesped, pk=pk)
    return JsonResponse({
        "nombre": huesped.nombre,
        "apellido": huesped.apellido,
        "correo": huesped.correo_electronico,
        "telefono": huesped.telefono,
    })

def huesped_edit(request, pk):
    huesped = get_object_or_404(Huesped, pk=pk)  # Obtener el huésped a editar
    habitacion = huesped.habitacion  # Asignamos la habitación asociada al huésped

    if request.method == 'POST':
        form = HuespedForm(request.POST, instance=huesped)  # Pasamos la instancia al formulario
        if form.is_valid():
            form.save()
            return redirect('huespedes:huesped_detail', pk=huesped.pk)  # Redirigir al detalle del huésped
    else:
        form = HuespedForm(instance=huesped)  # En GET, pasamos la instancia de huesped

    return render(request, 'huespedes/huesped_form.html', {
        'form': form,
        'habitacion': habitacion,
        'object': huesped  # Pasamos el objeto huesped a la plantilla
    })

@csrf_exempt
def agregar_huesped(request, habitacion_id):
    habitacion = get_object_or_404(Habitacion, pk=habitacion_id)
    if request.method == "POST":
        form = HuespedForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo_electronico')
            if Huesped.objects.filter(correo_electronico=correo).exists():
                return JsonResponse({"error": "Ya existe un huésped con este correo electrónico."}, status=400)

            huesped = form.save(commit=False)
            huesped.habitacion = habitacion
            huesped.save()

            if habitacion.huespedes.count() >= habitacion.capacidad:
                habitacion.disponible = False
                habitacion.save()

            return JsonResponse({"success": True, "message": "Huésped agregado exitosamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def editar_huesped(request, pk):
    huesped = get_object_or_404(Huesped, pk=pk)
    if request.method == "POST":
        form = HuespedForm(request.POST, instance=huesped)
        if form.is_valid():
            correo = form.cleaned_data.get('correo_electronico')
            if correo.lower() != huesped.correo_electronico.lower() and Huesped.objects.filter(correo_electronico__iexact=correo).exists():
                return JsonResponse({"error": "Datos inválidos", "errors": form.errors}, status=400)


            form.save()
            return JsonResponse({"success": True, "message": "Huésped actualizado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def eliminar_huesped(request, pk):
    if request.method == "POST":
        huesped = get_object_or_404(Huesped, pk=pk)
        habitacion = huesped.habitacion
        huesped.delete()

        if habitacion.huespedes.count() < habitacion.capacidad:
            habitacion.disponible = True
            habitacion.save()

        return JsonResponse({"success": True, "message": "Huésped eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)
