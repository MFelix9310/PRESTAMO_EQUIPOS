from django.db import models

class Persona(models.Model):
    CARRERA_CHOICES = [
        ('INDUSTRIAL', 'Ingeniería Industrial'),
        ('MECANICA', 'Ingeniería Mecánica'),
        ('MANTENIMIENTO', 'Ingeniería en Mantenimiento Industrial'),
        ('AUTOMOTRIZ', 'Ingeniería Automotriz'),
        ('PROFESOR', 'Profesor'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Número de Cédula")
    codigo_institucional = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código Institucional")
    carrera = models.CharField(max_length=20, choices=CARRERA_CHOICES, verbose_name="Carrera")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    def __str__(self):
        return f"{self.nombre} - {self.cedula}"
    
    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['nombre']

class Laboratorio(models.Model):
    TIPO_CHOICES = [
        ('LABORATORIO', 'Laboratorio'),
        ('TALLER', 'Taller'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Laboratorio")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Laboratorio")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Laboratorio"
        verbose_name_plural = "Laboratorios"
        ordering = ['nombre']

class Equipo(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código del Bien")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Bien")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name="equipos", verbose_name="Laboratorio")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['codigo']

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('PRESTADO', 'Prestado'),
        ('DEVUELTO', 'Devuelto'),
        ('DEVUELTO_PARCIAL', 'Devuelto Parcialmente'),
        ('RETRASADO', 'Retrasado'),
    ]
    
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="prestamos", verbose_name="Persona")
    fecha_prestamo = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Préstamo")
    fecha_devolucion_esperada = models.DateTimeField(verbose_name="Fecha de Devolución Esperada")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PRESTADO', verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    
    # Estos campos ahora son opcionales, ya que los equipos se manejan a través de DetallesPrestamo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="prestamos_antiguos", 
                              verbose_name="Equipo (Deprecado)", null=True, blank=True)
    fecha_devolucion_real = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Devolución Real")
    
    def __str__(self):
        return f"Préstamo a {self.persona.nombre} ({self.fecha_prestamo.strftime('%d/%m/%Y')})"
    
    def save(self, *args, **kwargs):
        # Mantener compatibilidad con el sistema antiguo
        if self.equipo and not self.pk:
            self.equipo.disponible = False
            self.equipo.save()
        elif self.equipo and self.estado == 'DEVUELTO' and self.fecha_devolucion_real:
            self.equipo.disponible = True
            self.equipo.save()
        
        # Verificar si todos los detalles están devueltos
        if self.pk:
            detalles = self.detalles.all()
            if detalles.exists():
                if detalles.filter(estado='PRESTADO').count() == 0:
                    self.estado = 'DEVUELTO'
                elif detalles.filter(estado='DEVUELTO').exists() and detalles.filter(estado='PRESTADO').exists():
                    self.estado = 'DEVUELTO_PARCIAL'
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']

class DetallePrestamo(models.Model):
    ESTADO_CHOICES = [
        ('PRESTADO', 'Prestado'),
        ('DEVUELTO', 'Devuelto'),
        ('RETRASADO', 'Retrasado'),
    ]
    
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name="detalles", verbose_name="Préstamo")
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="detalles_prestamo", verbose_name="Equipo")
    fecha_devolucion_real = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Devolución Real")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PRESTADO', verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    
    def __str__(self):
        return f"{self.equipo.nombre} - {self.get_estado_display()}"
    
    def save(self, *args, **kwargs):
        # Al crear un nuevo detalle, marcar el equipo como no disponible
        if not self.pk:
            self.equipo.disponible = False
            self.equipo.save()
        
        # Si se está devolviendo el equipo
        elif self.estado == 'DEVUELTO' and self.fecha_devolucion_real:
            self.equipo.disponible = True
            self.equipo.save()
            
            # Actualizar el estado del préstamo principal
            self.prestamo.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Detalle de Préstamo"
        verbose_name_plural = "Detalles de Préstamo"
        ordering = ['-prestamo__fecha_prestamo']
        unique_together = ['prestamo', 'equipo']
