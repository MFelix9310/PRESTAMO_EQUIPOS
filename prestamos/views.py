from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse

from .models import Persona, Laboratorio, Equipo, Prestamo, DetallePrestamo
from .forms import PersonaForm, LaboratorioForm, EquipoForm, PrestamoForm, BusquedaPersonaForm, BusquedaEquipoForm, DevolucionForm, DetallePrestamoDevolucionForm
from .pdf_utils import generar_pdf_prestamo

# Vistas para el Dashboard
def index(request ):
    prestamos_activos = Prestamo.objects.filter(estado='PRESTADO').count()
    equipos_disponibles = Equipo.objects.filter(disponible=True).count()
    total_personas = Persona.objects.count()
    total_equipos = Equipo.objects.count()
    ultimos_prestamos = Prestamo.objects.all().order_by('-fecha_prestamo')[:5]
    
    context = {
        'prestamos_activos': prestamos_activos,
        'equipos_disponibles': equipos_disponibles,
        'total_personas': total_personas,
        'total_equipos': total_equipos,
        'ultimos_prestamos': ultimos_prestamos,
    }
    
    return render(request, 'prestamos/index.html', context)

# Vistas para Personas
class PersonaListView(ListView):
    model = Persona
    template_name = 'prestamos/persona_list.html'
    context_object_name = 'personas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('busqueda', '')
        
        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) | 
                Q(cedula__icontains=busqueda) | 
                Q(codigo_institucional__icontains=busqueda)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        return context

class PersonaDetailView(DetailView):
    model = Persona
    template_name = 'prestamos/persona_detail.html'
    context_object_name = 'persona'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamos'] = Prestamo.objects.filter(persona=self.object).order_by('-fecha_prestamo')
        return context

class PersonaCreateView(CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'prestamos/persona_form.html'
    success_url = reverse_lazy('persona_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Persona registrada correctamente.')
        return super().form_valid(form)

class PersonaUpdateView(UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'prestamos/persona_form.html'
    
    def get_success_url(self):
        return reverse_lazy('persona_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Persona actualizada correctamente.')
        return super().form_valid(form)

class PersonaDeleteView(DeleteView):
    model = Persona
    template_name = 'prestamos/persona_confirm_delete.html'
    success_url = reverse_lazy('persona_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Persona eliminada correctamente.')
        return super().delete(request, *args, **kwargs)

def buscar_persona(request):
    if request.method == 'POST':
        form = BusquedaPersonaForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            try:
                persona = Persona.objects.get(cedula=cedula)
                return redirect('persona_detail', pk=persona.pk)
            except Persona.DoesNotExist:
                messages.error(request, f'No se encontró ninguna persona con cédula {cedula}.')
    else:
        form = BusquedaPersonaForm()
    
    return render(request, 'prestamos/buscar_persona.html', {'form': form})

# Vistas para Laboratorios
class LaboratorioListView(ListView):
    model = Laboratorio
    template_name = 'prestamos/laboratorio_list.html'
    context_object_name = 'laboratorios'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('busqueda', '')
        
        if busqueda:
            queryset = queryset.filter(nombre__icontains=busqueda)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        return context

class LaboratorioDetailView(DetailView):
    model = Laboratorio
    template_name = 'prestamos/laboratorio_detail.html'
    context_object_name = 'laboratorio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipos'] = Equipo.objects.filter(laboratorio=self.object)
        context['equipos_disponibles'] = Equipo.objects.filter(laboratorio=self.object, disponible=True).count()
        return context

class LaboratorioCreateView(CreateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = 'prestamos/laboratorio_form.html'
    success_url = reverse_lazy('laboratorio_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Laboratorio registrado correctamente.')
        return super().form_valid(form)

class LaboratorioUpdateView(UpdateView):
    model = Laboratorio
    form_class = LaboratorioForm
    template_name = 'prestamos/laboratorio_form.html'
    
    def get_success_url(self):
        return reverse_lazy('laboratorio_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Laboratorio actualizado correctamente.')
        return super().form_valid(form)

class LaboratorioDeleteView(DeleteView):
    model = Laboratorio
    template_name = 'prestamos/laboratorio_confirm_delete.html'
    success_url = reverse_lazy('laboratorio_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Laboratorio eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

# Vistas para Equipos
class EquipoListView(ListView):
    model = Equipo
    template_name = 'prestamos/equipo_list.html'
    context_object_name = 'equipos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('busqueda', '')
        laboratorio_id = self.request.GET.get('laboratorio', '')
        disponible = self.request.GET.get('disponible', '')
        
        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda) | 
                Q(nombre__icontains=busqueda)
            )
        
        if laboratorio_id:
            queryset = queryset.filter(laboratorio_id=laboratorio_id)
        
        if disponible == 'true':
            queryset = queryset.filter(disponible=True)
        elif disponible == 'false':
            queryset = queryset.filter(disponible=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['laboratorio_id'] = self.request.GET.get('laboratorio', '')
        context['disponible'] = self.request.GET.get('disponible', '')
        context['laboratorios'] = Laboratorio.objects.all()
        return context

class EquipoDetailView(DetailView):
    model = Equipo
    template_name = 'prestamos/equipo_detail.html'
    context_object_name = 'equipo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamos'] = Prestamo.objects.filter(equipo=self.object).order_by('-fecha_prestamo')
        return context

class EquipoCreateView(CreateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'prestamos/equipo_form.html'
    success_url = reverse_lazy('equipo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Equipo registrado correctamente.')
        return super().form_valid(form)

class EquipoUpdateView(UpdateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'prestamos/equipo_form.html'
    
    def get_success_url(self):
        return reverse_lazy('equipo_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Equipo actualizado correctamente.')
        return super().form_valid(form)

class EquipoDeleteView(DeleteView):
    model = Equipo
    template_name = 'prestamos/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipo_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Equipo eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

def buscar_equipo(request):
    if request.method == 'POST':
        form = BusquedaEquipoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            try:
                equipo = Equipo.objects.get(codigo=codigo)
                return redirect('equipo_detail', pk=equipo.pk)
            except Equipo.DoesNotExist:
                messages.error(request, f'No se encontró ningún equipo con código {codigo}.')
    else:
        form = BusquedaEquipoForm()
    
    return render(request, 'prestamos/buscar_equipo.html', {'form': form})

# Vistas para Préstamos
class PrestamoListView(ListView):
    model = Prestamo
    template_name = 'prestamos/prestamo_list.html'
    context_object_name = 'prestamos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get('busqueda', '')
        estado = self.request.GET.get('estado', '')
        
        if busqueda:
            queryset = queryset.filter(
                Q(persona__nombre__icontains=busqueda) | 
                Q(persona__cedula__icontains=busqueda) | 
                Q(equipo__codigo__icontains=busqueda) | 
                Q(equipo__nombre__icontains=busqueda)
            )
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda'] = self.request.GET.get('busqueda', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['estados'] = [
            ('PRESTADO', 'Prestado'),
            ('DEVUELTO', 'Devuelto'),
            ('RETRASADO', 'Retrasado')
        ]
        return context

class PrestamoDetailView(DetailView):
    model = Prestamo
    template_name = 'prestamos/prestamo_detail.html'
    context_object_name = 'prestamo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los detalles del préstamo
        context['detalles'] = self.object.detalles.all().select_related('equipo')
        return context

class PrestamoCreateView(CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/prestamo_form.html'
    success_url = reverse_lazy('prestamo_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            if 'buscar_persona' in self.request.POST:
                kwargs['data'] = self.request.POST.copy()
                kwargs['data']['buscar_persona'] = True
        return kwargs
    
    def form_valid(self, form):
        # Guardar el préstamo
        prestamo = form.save(commit=False)
        prestamo.estado = 'PRESTADO'
        prestamo.save()
        
        # Guardar los detalles del préstamo para cada equipo seleccionado
        equipos_seleccionados = form.cleaned_data['equipos']
        for equipo in equipos_seleccionados:
            # Verificar si el equipo está disponible
            if not equipo.disponible:
                messages.error(self.request, f'El equipo {equipo.nombre} no está disponible actualmente.')
                # Si hay un error, eliminar el préstamo y redirigir
                prestamo.delete()
                return self.form_invalid(form)
            
            # Crear el detalle del préstamo
            DetallePrestamo.objects.create(
                prestamo=prestamo,
                equipo=equipo,
                estado='PRESTADO'
            )
        
        messages.success(self.request, 'Préstamo registrado correctamente.')
        return redirect('prestamo_detail', pk=prestamo.pk)

class PrestamoUpdateView(UpdateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'prestamos/prestamo_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            if 'buscar_persona' in self.request.POST:
                kwargs['data'] = self.request.POST.copy()
                kwargs['data']['buscar_persona'] = True
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('prestamo_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        prestamo = self.get_object()
        
        # Obtener los equipos actualmente prestados
        detalles_actuales = prestamo.detalles.filter(estado='PRESTADO')
        equipos_actuales = {detalle.equipo.pk for detalle in detalles_actuales}
        
        # Obtener los nuevos equipos seleccionados
        equipos_nuevos = {equipo.pk for equipo in form.cleaned_data['equipos']}
        
        # Equipos a añadir: están en los nuevos pero no en los actuales
        equipos_a_anadir = equipos_nuevos - equipos_actuales
        
        # Equipos a quitar: están en los actuales pero no en los nuevos
        equipos_a_quitar = equipos_actuales - equipos_nuevos
        
        # Guardar los cambios básicos del préstamo
        prestamo = form.save()
        
        # Procesar equipos a añadir
        for equipo_id in equipos_a_anadir:
            equipo = Equipo.objects.get(pk=equipo_id)
            
            # Verificar disponibilidad
            if not equipo.disponible:
                messages.error(self.request, f'El equipo {equipo.nombre} no está disponible actualmente.')
                continue
            
            # Crear nuevo detalle
            DetallePrestamo.objects.create(
                prestamo=prestamo,
                equipo=equipo,
                estado='PRESTADO'
            )
        
        # Procesar equipos a quitar (marcarlos como devueltos)
        for equipo_id in equipos_a_quitar:
            detalle = detalles_actuales.get(equipo_id=equipo_id)
            detalle.estado = 'DEVUELTO'
            detalle.fecha_devolucion_real = timezone.now()
            detalle.save()
        
        messages.success(self.request, 'Préstamo actualizado correctamente.')
        return redirect('prestamo_detail', pk=prestamo.pk)

class PrestamoDeleteView(DeleteView):
    model = Prestamo
    template_name = 'prestamos/prestamo_confirm_delete.html'
    success_url = reverse_lazy('prestamo_list')
    
    def delete(self, request, *args, **kwargs):
        prestamo = self.get_object()
        
        # Si el préstamo está activo, liberar los equipos
        if prestamo.estado == 'PRESTADO':
            detalles = prestamo.detalles.filter(estado='PRESTADO')
            for detalle in detalles:
                equipo = detalle.equipo
                equipo.disponible = True
                equipo.save()
        
        messages.success(request, 'Préstamo eliminado correctamente.')
        return super().delete(request, *args, **kwargs)

def devolver_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    
    if prestamo.estado == 'DEVUELTO':
        messages.error(request, 'Este préstamo ya ha sido devuelto completamente.')
        return redirect('prestamo_detail', pk=prestamo.pk)
    
    if request.method == 'POST':
        form = DevolucionForm(request.POST)
        if form.is_valid():
            # Marcar todos los detalles como devueltos
            detalles = prestamo.detalles.filter(estado='PRESTADO')
            for detalle in detalles:
                detalle.estado = 'DEVUELTO'
                detalle.fecha_devolucion_real = timezone.now()
                detalle.observaciones = form.cleaned_data.get('observaciones')
                detalle.save()
            
            # El estado del préstamo se actualizará automáticamente en el save() del DetallePrestamo
            messages.success(request, 'Todos los equipos han sido devueltos correctamente.')
            return redirect('prestamo_detail', pk=prestamo.pk)
    else:
        form = DevolucionForm()
    
    return render(request, 'prestamos/devolver_prestamo.html', {
        'form': form,
        'prestamo': prestamo
    })

def devolver_equipo(request, prestamo_id, detalle_id):
    detalle = get_object_or_404(DetallePrestamo, id=detalle_id, prestamo_id=prestamo_id, estado='PRESTADO')
    
    if request.method == 'POST':
        form = DetallePrestamoDevolucionForm(request.POST, instance=detalle)
        if form.is_valid():
            # Actualizar el detalle
            detalle = form.save(commit=False)
            detalle.estado = 'DEVUELTO'
            detalle.fecha_devolucion_real = timezone.now()
            detalle.save()  # Esto también actualizará el estado del préstamo
            
            messages.success(request, f'El equipo {detalle.equipo.nombre} ha sido devuelto correctamente.')
            return redirect('prestamo_detail', pk=prestamo_id)
    else:
        form = DetallePrestamoDevolucionForm(instance=detalle)
    
    return render(request, 'prestamos/devolver_equipo.html', {
        'form': form,
        'detalle': detalle,
        'prestamo': detalle.prestamo
    })

# Vista para generar PDF
def generar_pdf_prestamo_view(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    download = request.GET.get('download', False)
    return generar_pdf_prestamo(prestamo, download)
