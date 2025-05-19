from django import forms
from django.db import models
from .models import Persona, Equipo, Prestamo, Laboratorio, DetallePrestamo
from django.utils import timezone
from datetime import timedelta

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['nombre', 'cedula', 'codigo_institucional', 'carrera']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de cédula'}),
            'codigo_institucional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código institucional (opcional para profesores)'}),
            'carrera': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit() or len(cedula) != 10:
            raise forms.ValidationError("La cédula debe contener 10 dígitos numéricos.")
        return cedula
    
    def clean(self):
        cleaned_data = super().clean()
        carrera = cleaned_data.get('carrera')
        codigo_institucional = cleaned_data.get('codigo_institucional')
        
        if carrera != 'PROFESOR' and not codigo_institucional:
            self.add_error('codigo_institucional', "El código institucional es requerido para estudiantes.")
        
        return cleaned_data

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['codigo', 'nombre', 'descripcion', 'laboratorio', 'disponible']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del bien'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del bien'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
            'laboratorio': forms.Select(attrs={'class': 'form-select'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = ['nombre', 'tipo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del laboratorio'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
        }

class MultipleEquipoField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, equipo):
        return f"{equipo.codigo} - {equipo.nombre} ({equipo.laboratorio.nombre})"

class PrestamoForm(forms.ModelForm):
    cedula_busqueda = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por cédula'})
    )
    
    equipos = MultipleEquipoField(
        queryset=Equipo.objects.filter(disponible=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'size': '5',
            'multiple': 'multiple',
            'data-placeholder': 'Seleccione uno o más equipos'
        }),
        required=True,
        label="Equipos (presione Ctrl para seleccionar varios)"
    )
    
    class Meta:
        model = Prestamo
        fields = ['persona', 'fecha_devolucion_esperada', 'observaciones']
        widgets = {
            'persona': forms.Select(attrs={'class': 'form-select'}),
            'fecha_devolucion_esperada': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Observaciones (opcional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha de devolución por defecto (una semana)
        if not self.instance.pk:
            self.initial['fecha_devolucion_esperada'] = timezone.now() + timedelta(days=7)
        else:
            # Si es edición, cargar los equipos asociados
            detalles = self.instance.detalles.filter(estado='PRESTADO')
            if detalles.exists():
                self.initial['equipos'] = [d.equipo.pk for d in detalles]
                # Incluir equipos que ya están en préstamo para este préstamo específico
                self.fields['equipos'].queryset = Equipo.objects.filter(
                    models.Q(disponible=True) | 
                    models.Q(detalles_prestamo__prestamo=self.instance, detalles_prestamo__estado='PRESTADO')
                ).distinct()

class BusquedaPersonaForm(forms.Form):
    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la cédula'})
    )

class BusquedaEquipoForm(forms.Form):
    codigo = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el código del equipo'})
    )

class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones sobre la devolución (opcional)'}),
        }

class DetallePrestamoDevolucionForm(forms.ModelForm):
    class Meta:
        model = DetallePrestamo
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Observaciones sobre la devolución (opcional)'}),
        }
