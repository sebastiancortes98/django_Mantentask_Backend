from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import (
    Usuario, TipoUsuario, NivelAcceso, Sucursal, 
    Estado, Maquina, Solicitud, Informe, Task
)
from .serializers import (
    UsuarioSerializer, TipoUsuarioSerializer, NivelAccesoSerializer,
    SucursalSerializer, EstadoSerializer, MaquinaSerializer,
    SolicitudSerializer, SolicitudCreateUpdateSerializer,
    InformeSerializer, InformeCreateUpdateSerializer, TaskSerializer
)
from .utils import generar_pdf_informe

logger = logging.getLogger(__name__)


class TipoUsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar tipos de usuario"""
    queryset = TipoUsuario.objects.all()
    serializer_class = TipoUsuarioSerializer
    permission_classes = [AllowAny]


class NivelAccesoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar niveles de acceso"""
    queryset = NivelAcceso.objects.all()
    serializer_class = NivelAccesoSerializer
    permission_classes = [AllowAny]


class SucursalViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar sucursales"""
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_sucursal']
    ordering_fields = ['nombre_sucursal']


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo_tipo_usuario', 'codigo_nivel_acceso', 'codigo_sucursal', 'is_active']
    search_fields = ['username', 'first_name', 'apellido_paterno', 'apellido_materno', 'correo_electronico']
    ordering_fields = ['date_joined', 'username']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get'])
    def ingenieros(self, request):
        """Listar solo ingenieros"""
        ingenieros = self.queryset.filter(codigo_tipo_usuario=1)
        serializer = self.get_serializer(ingenieros, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def encargados(self, request):
        """Listar solo encargados"""
        encargados = self.queryset.filter(codigo_tipo_usuario=2)
        serializer = self.get_serializer(encargados, many=True)
        return Response(serializer.data)


class EstadoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar estados"""
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [AllowAny]


class MaquinaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar máquinas"""
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo_sucursal', 'marca']
    search_fields = ['modelo', 'marca']
    ordering_fields = ['fecha_compra', 'fecha_instalacion', 'fecha_ultima_mantencion']
    
    @action(detail=False, methods=['get'])
    def por_sucursal(self, request):
        """Listar máquinas agrupadas por sucursal"""
        sucursal_id = request.query_params.get('sucursal')
        if sucursal_id:
            maquinas = self.queryset.filter(codigo_sucursal=sucursal_id)
            serializer = self.get_serializer(maquinas, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro sucursal requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def registrar_mantenimiento(self, request, pk=None):
        """Registrar fecha de último mantenimiento"""
        maquina = self.get_object()
        maquina.fecha_ultima_mantencion = timezone.now().date()
        maquina.save()
        serializer = self.get_serializer(maquina)
        return Response(serializer.data)


class SolicitudViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar solicitudes (tickets)"""
    queryset = Solicitud.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo_estado', 'codigo_maquinaria', 'id_usuario']
    search_fields = ['descripcion']
    ordering_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitudCreateUpdateSerializer
        return SolicitudSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear solicitud y enviar notificación"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Enviar notificación por correo
        try:
            self._enviar_notificacion_nueva_solicitud(solicitud)
        except Exception as e:
            print(f"Error al enviar notificación: {e}")
        
        # Retornar respuesta con serializer completo
        response_serializer = SolicitudSerializer(solicitud)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Actualizar solicitud y notificar cambios de estado"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        estado_anterior = instance.codigo_estado
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Si cambió el estado, enviar notificación
        if estado_anterior != solicitud.codigo_estado:
            try:
                self._enviar_notificacion_cambio_estado(solicitud, estado_anterior)
            except Exception as e:
                print(f"Error al enviar notificación: {e}")
        
        response_serializer = SolicitudSerializer(solicitud)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Listar solicitudes pendientes"""
        solicitudes = self.queryset.filter(codigo_estado__in=[1, 2])
        serializer = SolicitudSerializer(solicitudes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completadas(self, request):
        """Listar solicitudes completadas"""
        solicitudes = self.queryset.filter(codigo_estado=3)
        serializer = SolicitudSerializer(solicitudes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de solicitud"""
        solicitud = self.get_object()
        nuevo_estado_id = request.data.get('codigo_estado')
        
        if not nuevo_estado_id:
            return Response(
                {'error': 'codigo_estado requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nuevo_estado = Estado.objects.get(codigo_estado=nuevo_estado_id)
            estado_anterior = solicitud.codigo_estado
            solicitud.codigo_estado = nuevo_estado
            solicitud.save()
            
            # Enviar notificación
            try:
                self._enviar_notificacion_cambio_estado(solicitud, estado_anterior)
            except Exception as e:
                print(f"Error al enviar notificación: {e}")
            
            serializer = SolicitudSerializer(solicitud)
            return Response(serializer.data)
        except Estado.DoesNotExist:
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _enviar_notificacion_nueva_solicitud(self, solicitud):
        """Enviar correo de notificación por nueva solicitud"""
        try:
            subject = f'Nueva Solicitud #{solicitud.codigo_solicitud}'
            message = f"""
            Se ha creado una nueva solicitud de mantenimiento.
            
            Solicitud: #{solicitud.codigo_solicitud}
            Máquina: {solicitud.codigo_maquinaria.marca} {solicitud.codigo_maquinaria.modelo}
            Usuario: {solicitud.id_usuario.get_full_name()}
            Descripción: {solicitud.descripcion}
            Estado: {solicitud.codigo_estado.nombre_estado}
            Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
            """
            
            # Enviar a administradores o ingenieros
            destinatarios = Usuario.objects.filter(
                codigo_tipo_usuario=1,  # Ingenieros
                is_active=True
            ).values_list('correo_electronico', flat=True)
            
            if destinatarios:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    list(destinatarios),
                    fail_silently=False,
                )
                logger.info(f"Notificación enviada a {len(destinatarios)} ingenieros para solicitud #{solicitud.codigo_solicitud}")
        except Exception as e:
            logger.error(f"Error enviando notificación de nueva solicitud: {str(e)}")
            # No interrumpir el flujo si falla el email
    
    def _enviar_notificacion_cambio_estado(self, solicitud, estado_anterior):
        """Enviar correo de notificación por cambio de estado"""
        try:
            subject = f'Cambio de Estado - Solicitud #{solicitud.codigo_solicitud}'
            message = f"""
            La solicitud de mantenimiento ha cambiado de estado.
            
            Solicitud: #{solicitud.codigo_solicitud}
            Estado anterior: {estado_anterior.nombre_estado}
            Estado nuevo: {solicitud.codigo_estado.nombre_estado}
            Máquina: {solicitud.codigo_maquinaria.marca} {solicitud.codigo_maquinaria.modelo}
            Fecha actualización: {solicitud.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}
            """
            
            # Enviar al usuario que creó la solicitud
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [solicitud.id_usuario.correo_electronico],
                fail_silently=False,
            )
            logger.info(f"Notificación de cambio de estado enviada a {solicitud.id_usuario.correo_electronico} para solicitud #{solicitud.codigo_solicitud}")
        except Exception as e:
            logger.error(f"Error enviando notificación de cambio de estado: {str(e)}")
            # No interrumpir el flujo si falla el email


class InformeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar informes"""
    queryset = Informe.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['codigo_maquinaria', 'id_usuario']
    ordering_fields = ['fecha_informe']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InformeCreateUpdateSerializer
        return InformeSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear informe y generar PDF automáticamente"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        informe = serializer.save()
        
        # Generar PDF automáticamente
        try:
            generar_pdf_informe(informe)
        except Exception as e:
            print(f"Error al generar PDF: {e}")
        
        response_serializer = InformeSerializer(informe, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def descargar_pdf(self, request, pk=None):
        """Descargar PDF del informe"""
        informe = self.get_object()
        
        if not informe.archivo_pdf:
            # Generar PDF si no existe
            try:
                generar_pdf_informe(informe)
            except Exception as e:
                return Response(
                    {'error': f'Error al generar PDF: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        try:
            return FileResponse(
                informe.archivo_pdf.open('rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f'informe_{informe.codigo_solicitud.codigo_solicitud}.pdf'
            )
        except Exception as e:
            return Response(
                {'error': f'Error al descargar PDF: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def regenerar_pdf(self, request, pk=None):
        """Regenerar PDF del informe"""
        informe = self.get_object()
        
        try:
            generar_pdf_informe(informe)
            serializer = InformeSerializer(informe, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error al regenerar PDF: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def enviar_por_correo(self, request, pk=None):
        """Enviar informe por correo electrónico"""
        informe = self.get_object()
        destinatario = request.data.get('email')
        
        if not destinatario:
            return Response(
                {'error': 'Email requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Asegurar que existe el PDF
            if not informe.archivo_pdf:
                generar_pdf_informe(informe)
            
            subject = f'Informe de Mantenimiento - Solicitud #{informe.codigo_solicitud.codigo_solicitud}'
            message = f"""
            Adjunto encontrará el informe de mantenimiento.
            
            Solicitud: #{informe.codigo_solicitud.codigo_solicitud}
            Máquina: {informe.codigo_maquinaria.marca} {informe.codigo_maquinaria.modelo}
            Fecha: {informe.fecha_informe.strftime('%d/%m/%Y %H:%M')}
            """
            
            email = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [destinatario],
                fail_silently=False,
            )
            
            # Adjuntar PDF (requiere configuración adicional)
            # Ver implementación en utils.py
            
            return Response({'mensaje': 'Correo enviado exitosamente'})
        except Exception as e:
            return Response(
                {'error': f'Error al enviar correo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ViewSet legacy para compatibilidad
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]
