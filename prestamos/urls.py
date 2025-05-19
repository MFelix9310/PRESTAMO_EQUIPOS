from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.index, name='index'),
    
    # Personas
    path('personas/', views.PersonaListView.as_view(), name='persona_list'),
    path('personas/crear/', views.PersonaCreateView.as_view(), name='persona_create'),
    path('personas/<int:pk>/', views.PersonaDetailView.as_view(), name='persona_detail'),
    path('personas/<int:pk>/editar/', views.PersonaUpdateView.as_view(), name='persona_update'),
    path('personas/<int:pk>/eliminar/', views.PersonaDeleteView.as_view(), name='persona_delete'),
    path('personas/buscar/', views.buscar_persona, name='buscar_persona'),
    
    # Laboratorios
    path('laboratorios/', views.LaboratorioListView.as_view(), name='laboratorio_list'),
    path('laboratorios/crear/', views.LaboratorioCreateView.as_view(), name='laboratorio_create'),
    path('laboratorios/<int:pk>/', views.LaboratorioDetailView.as_view(), name='laboratorio_detail'),
    path('laboratorios/<int:pk>/editar/', views.LaboratorioUpdateView.as_view(), name='laboratorio_update'),
    path('laboratorios/<int:pk>/eliminar/', views.LaboratorioDeleteView.as_view(), name='laboratorio_delete'),
    
    # Equipos
    path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
    path('equipos/crear/', views.EquipoCreateView.as_view(), name='equipo_create'),
    path('equipos/<int:pk>/', views.EquipoDetailView.as_view(), name='equipo_detail'),
    path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_delete'),
    path('equipos/buscar/', views.buscar_equipo, name='buscar_equipo'),
    
    # Préstamos
    path('prestamos/', views.PrestamoListView.as_view(), name='prestamo_list'),
    path('prestamos/crear/', views.PrestamoCreateView.as_view(), name='prestamo_create'),
    path('prestamos/<int:pk>/', views.PrestamoDetailView.as_view(), name='prestamo_detail'),
    path('prestamos/<int:pk>/editar/', views.PrestamoUpdateView.as_view(), name='prestamo_update'),
    path('prestamos/<int:pk>/eliminar/', views.PrestamoDeleteView.as_view(), name='prestamo_delete'),
    path('prestamos/<int:pk>/devolver/', views.devolver_prestamo, name='devolver_prestamo'),
    path('prestamos/<int:prestamo_id>/devolver-equipo/<int:detalle_id>/', views.devolver_equipo, name='devolver_equipo'),
    path('prestamos/<int:pk>/pdf/', views.generar_pdf_prestamo_view, name='generar_pdf_prestamo'),
]
