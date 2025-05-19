from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from prestamos.models import Equipo, Prestamo
from .serializers import (
    EquipoSerializer, 
    PrestamoSerializer, 
    PrestamoCreateSerializer
)

class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        equipos = Equipo.objects.filter(disponible=True)
        serializer = self.get_serializer(equipos, many=True)
        return Response(serializer.data)

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all()
    serializer_class = PrestamoSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PrestamoCreateSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def usuario(self, request):
        email = request.query_params.get('email', None)
        if email is None:
            return Response(
                {"error": "Se requiere el parámetro email"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prestamos = Prestamo.objects.filter(persona__cedula=email)
        serializer = self.get_serializer(prestamos, many=True)
        return Response(serializer.data) 