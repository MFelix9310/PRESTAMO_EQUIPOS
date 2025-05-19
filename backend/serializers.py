from rest_framework import serializers
from prestamos.models import Equipo, Prestamo, Persona, DetallePrestamo

class EquipoSerializer(serializers.ModelSerializer):
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    
    class Meta:
        model = Equipo
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'disponible', 'laboratorio', 'laboratorio_nombre']

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

class DetallePrestamoSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)
    equipo_codigo = serializers.CharField(source='equipo.codigo', read_only=True)
    
    class Meta:
        model = DetallePrestamo
        fields = '__all__'

class PrestamoCreateSerializer(serializers.Serializer):
    equipo = serializers.PrimaryKeyRelatedField(queryset=Equipo.objects.all())
    solicitante = serializers.CharField(max_length=100)
    correo = serializers.EmailField()
    fecha_prestamo = serializers.DateField()
    fecha_devolucion = serializers.DateField()
    motivo = serializers.CharField(allow_blank=True, required=False)
    
    def create(self, validated_data):
        # Verificar si la persona existe o crearla
        nombre_solicitante = validated_data.get('solicitante')
        correo = validated_data.get('correo')
        
        # Buscar o crear persona
        persona, created = Persona.objects.get_or_create(
            cedula=correo,  # Usamos el correo como cedula temporal
            defaults={
                'nombre': nombre_solicitante,
                'carrera': 'PROFESOR',  # Valor por defecto
            }
        )
        
        # Crear el préstamo
        prestamo = Prestamo.objects.create(
            persona=persona,
            fecha_devolucion_esperada=validated_data.get('fecha_devolucion'),
            observaciones=validated_data.get('motivo', '')
        )
        
        # Crear el detalle del préstamo
        DetallePrestamo.objects.create(
            prestamo=prestamo,
            equipo=validated_data.get('equipo'),
            estado='PRESTADO'
        )
        
        return prestamo

class PrestamoSerializer(serializers.ModelSerializer):
    persona_nombre = serializers.CharField(source='persona.nombre', read_only=True)
    detalles = DetallePrestamoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prestamo
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Si hay detalles de préstamo, usar el primer detalle para simplificar la representación
        if instance.detalles.exists():
            detalle = instance.detalles.first()
            representation['equipo'] = {
                'id': detalle.equipo.id,
                'nombre': detalle.equipo.nombre,
                'codigo': detalle.equipo.codigo,
            }
            representation['devuelto'] = detalle.estado == 'DEVUELTO'
        elif instance.equipo:  # Sistema antiguo
            representation['equipo'] = {
                'id': instance.equipo.id,
                'nombre': instance.equipo.nombre,
                'codigo': instance.equipo.codigo,
            }
            representation['devuelto'] = instance.estado == 'DEVUELTO'
        
        return representation 