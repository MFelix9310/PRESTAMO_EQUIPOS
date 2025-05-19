from django.contrib import admin
from .models import Persona, Laboratorio, Equipo, Prestamo

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cedula', 'codigo_institucional', 'carrera', 'fecha_registro')
    search_fields = ('nombre', 'cedula', 'codigo_institucional')
    list_filter = ('carrera',)

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'descripcion')
    search_fields = ('nombre',)
    list_filter = ('tipo',)

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'laboratorio', 'disponible', 'fecha_registro')
    search_fields = ('codigo', 'nombre')
    list_filter = ('laboratorio', 'disponible')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('persona', 'equipo', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado')
    search_fields = ('persona__nombre', 'equipo__nombre', 'equipo__codigo')
    list_filter = ('estado', 'fecha_prestamo')
    date_hierarchy = 'fecha_prestamo'
