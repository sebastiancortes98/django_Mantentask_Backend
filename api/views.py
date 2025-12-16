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
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthenticatedOrReadOnly, IsEngineer
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo_tipo_usuario', 'codigo_nivel_acceso', 'codigo_sucursal', 'is_active']
    search_fields = ['username', 'first_name', 'apellido_paterno', 'apellido_materno', 'correo_electronico']
    ordering_fields = ['date_joined', 'username']
    
    def get_permissions(self):
        """
        Permitir GET sin autenticación para ciertos datos
        POST requiere autenticación
        PUT, PATCH, DELETE solo para admins
        """
        if self.action == 'create':
            return [AllowAny()]  # Registro público
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]  # Solo admin puede editar usuarios
        elif self.action in ['me', 'ingenieros', 'encargados']:
            return [IsAuthenticated()]  # Solo autenticados
        else:
            return [AllowAny()]  # GET sin autenticación
    
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
    
    def get_permissions(self):
        """
        Permitir GET sin autenticación
        Requerir autenticación para POST, PUT, PATCH, DELETE
        """
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo_estado', 'codigo_maquinaria', 'id_usuario', 'codigo_maquinaria__codigo_sucursal']
    search_fields = ['descripcion']
    ordering_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_queryset(self):
        """Optimizar queries con select_related para evitar N+1"""
        queryset = Solicitud.objects.select_related(
            'id_usuario',
            'ingeniero_asignado',
            'codigo_maquinaria',
            'codigo_maquinaria__codigo_sucursal',
            'codigo_estado'
        )
        
        # Filtros personalizados por query params
        user = self.request.user if hasattr(self, 'request') else None
        if user and user.is_authenticated:
            # Filtro por estado usando aliases
            if self.request.query_params.get('pendientes'):
                queryset = queryset.filter(codigo_estado=1)
            elif self.request.query_params.get('en_proceso'):
                queryset = queryset.filter(codigo_estado=2)
            elif self.request.query_params.get('completadas'):
                queryset = queryset.filter(codigo_estado=3)
            
            # Filtro por ingeniero
            ingeniero_id = self.request.query_params.get('id_ingeniero')
            if ingeniero_id:
                queryset = queryset.filter(ingeniero_asignado__id_usuario=ingeniero_id)
        
        return queryset
    
    def get_permissions(self):
        """
        GET: Autenticados
        POST: Autenticados
        PUT/PATCH: Solo admin o el usuario propietario
        DELETE: Solo admin
        """
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated()]  # Validar en perform_update
        elif self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitudCreateUpdateSerializer
        return SolicitudSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear solicitud y enviar notificación"""
        data = request.data.copy()
        # Forzar el usuario autenticado y estado inicial pendiente (1) si no viene
        data.setdefault('id_usuario', request.user.id_usuario)
        data.setdefault('codigo_estado', 1)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Enviar notificación por correo (DESHABILITADO temporalmente por timeout SMTP)
        # try:
        #     self._enviar_notificacion_nueva_solicitud(solicitud)
        # except Exception as e:
        #     print(f"Error al enviar notificación: {e}")
        
        # Retornar respuesta con serializer completo
        response_serializer = SolicitudSerializer(solicitud)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='por-encargados')
    def por_encargados(self, request):
        """Listar solicitudes creadas por usuarios Encargados (tipo 2). Opcional: ?codigo_sucursal=ID"""
        qs = self.queryset.filter(id_usuario__codigo_tipo_usuario=2)
        codigo_sucursal = request.query_params.get('codigo_sucursal')
        if codigo_sucursal:
            qs = qs.filter(codigo_maquinaria__codigo_sucursal=codigo_sucursal)
        serializer = SolicitudSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='por-sucursal')
    def por_sucursal(self, request):
        """Listar solicitudes por sucursal: requiere ?codigo_sucursal=ID"""
        codigo_sucursal = request.query_params.get('codigo_sucursal')
        if not codigo_sucursal:
            return Response({'error': 'Parametro codigo_sucursal requerido'}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.queryset.filter(codigo_maquinaria__codigo_sucursal=codigo_sucursal)
        serializer = SolicitudSerializer(qs, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Actualizar solicitud y notificar cambios de estado"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        estado_anterior = instance.codigo_estado

        data = request.data.copy()
        # No permitir cambiar el usuario dueño desde el frontend
        data['id_usuario'] = instance.id_usuario.id_usuario

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        # Si cambió el estado, enviar notificación (DESHABILITADO temporalmente por timeout SMTP)
        # if estado_anterior != solicitud.codigo_estado:
        #     try:
        #         self._enviar_notificacion_cambio_estado(solicitud, estado_anterior)
        #     except Exception as e:
        #         print(f"Error al enviar notificación: {e}")
        
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
        """
        Cambiar estado de solicitud
        
        Reglas de negocio:
        - Encargados/Admin: pueden cambiar cualquier solicitud a cualquier estado
        - Ingenieros: solo pueden cambiar solicitudes asignadas a ellos
        - Ingenieros: solo pueden avanzar estados (1→2→3), no retroceder
        
        Estados válidos:
        1 - Pendiente
        2 - En Proceso
        3 - Completada
        """
        solicitud = self.get_object()
        nuevo_estado_id = request.data.get('codigo_estado')
        
        # Validar que viene el estado
        if not nuevo_estado_id:
            return Response(
                {'error': 'codigo_estado requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el estado sea válido (1, 2 o 3)
        try:
            nuevo_estado_id = int(nuevo_estado_id)
            if nuevo_estado_id not in [1, 2, 3]:
                return Response(
                    {'error': 'Estado debe ser 1 (Pendiente), 2 (En Proceso) o 3 (Completada)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'codigo_estado debe ser un número entero'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        estado_anterior_id = solicitud.codigo_estado.codigo_estado
        
        # Validar permisos según tipo de usuario
        es_admin = user.codigo_nivel_acceso == 4
        es_encargado = user.codigo_tipo_usuario == 2
        es_ingeniero = user.codigo_tipo_usuario == 1
        es_ingeniero_asignado = solicitud.ingeniero_asignado and solicitud.ingeniero_asignado.id_usuario == user.id_usuario
        
        # Admin y encargados pueden cambiar cualquier solicitud a cualquier estado
        if es_admin or es_encargado:
            pass  # Tienen permiso total
        # Ingenieros solo pueden cambiar solicitudes asignadas a ellos
        elif es_ingeniero:
            if not es_ingeniero_asignado:
                return Response(
                    {'error': 'Solo puedes cambiar el estado de solicitudes asignadas a ti'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            # Validar que solo avancen estados (no retrocedan)
            if nuevo_estado_id < estado_anterior_id:
                return Response(
                    {'error': 'No puedes retroceder el estado de una solicitud'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'No tienes permiso para cambiar el estado de solicitudes'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el objeto Estado
        try:
            nuevo_estado = Estado.objects.get(codigo_estado=nuevo_estado_id)
            estado_anterior = solicitud.codigo_estado
            solicitud.codigo_estado = nuevo_estado
            solicitud.save()
            
            logger.info(f"Usuario {user.username} cambió estado de solicitud #{solicitud.codigo_solicitud} de {estado_anterior.nombre_estado} a {nuevo_estado.nombre_estado}")
            
            # Enviar notificación (DESHABILITADO temporalmente por timeout SMTP)
            # try:
            #     self._enviar_notificacion_cambio_estado(solicitud, estado_anterior)
            # except Exception as e:
            #     logger.error(f"Error al enviar notificación: {e}")
            
            serializer = SolicitudSerializer(solicitud)
            response_data = serializer.data
            response_data['mensaje'] = f'Estado actualizado correctamente a {nuevo_estado.nombre_estado}'
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Estado.DoesNotExist:
            return Response(
                {'error': 'Estado no válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def asignar_ingeniero(self, request, pk=None):
        """
        Asignar ingeniero a una solicitud
        
        Solo accesible para encargados y administradores
        
        Request body:
        {
            "id_ingeniero": 5
        }
        """
        solicitud = self.get_object()
        id_ingeniero = request.data.get('id_ingeniero')
        
        # Validar permiso: solo encargados y admin
        user = request.user
        es_admin = user.codigo_nivel_acceso == 4
        es_encargado = user.codigo_tipo_usuario == 2
        
        if not (es_admin or es_encargado):
            return Response(
                {'error': 'Solo encargados y administradores pueden asignar ingenieros'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar que viene el id_ingeniero
        if not id_ingeniero:
            return Response(
                {'error': 'id_ingeniero requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el ingeniero existe y es ingeniero (tipo 1)
        try:
            ingeniero = Usuario.objects.get(
                id_usuario=id_ingeniero,
                codigo_tipo_usuario=1,  # Solo ingenieros
                is_active=True
            )
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Ingeniero no encontrado o no válido'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asignar ingeniero
        solicitud.ingeniero_asignado = ingeniero
        solicitud.save()
        
        logger.info(f"Usuario {user.username} asignó ingeniero {ingeniero.username} a solicitud #{solicitud.codigo_solicitud}")
        
        serializer = SolicitudSerializer(solicitud)
        response_data = serializer.data
        response_data['mensaje'] = f'Ingeniero {ingeniero.get_full_name()} asignado correctamente'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
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
                    fail_silently=True,
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
                fail_silently=True,
            )
            logger.info(f"Notificación de cambio de estado enviada a {solicitud.id_usuario.correo_electronico} para solicitud #{solicitud.codigo_solicitud}")
        except Exception as e:
            logger.error(f"Error enviando notificación de cambio de estado: {str(e)}")
            # No interrumpir el flujo si falla el email


class InformeViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar informes"""
    queryset = Informe.objects.select_related('codigo_solicitud', 'codigo_maquinaria', 'id_usuario')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['codigo_solicitud', 'codigo_maquinaria', 'id_usuario']
    ordering_fields = ['fecha_informe']
    
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsEngineer()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtros adicionales via query params
        codigo_informe = self.request.query_params.get('codigo_informe')
        codigo_solicitud = self.request.query_params.get('codigo_solicitud')
        codigo_maquinaria = self.request.query_params.get('codigo_maquinaria')
        fecha_informe = self.request.query_params.get('fecha_informe')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if codigo_informe:
            qs = qs.filter(codigo_solicitud__codigo_solicitud=codigo_informe)
        if codigo_solicitud:
            qs = qs.filter(codigo_solicitud__codigo_solicitud=codigo_solicitud)
        if codigo_maquinaria:
            qs = qs.filter(codigo_maquinaria__codigo_maquinaria=codigo_maquinaria)
        if fecha_informe:
            qs = qs.filter(fecha_informe__date=fecha_informe)
        if fecha_desde:
            qs = qs.filter(fecha_informe__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_informe__date__lte=fecha_hasta)
        return qs
    
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
        """Enviar informe por correo electrónico con PDF adjunto"""
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
        """Enviar informe por correo electrónico con PDF adjunto"""
        informe = self.get_object()
        destinatario = request.data.get('email')
        
        if not destinatario:
            return Response(
                {'error': 'Email requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.core.mail import EmailMessage
            
            # Asegurar que existe el PDF
            if not informe.archivo_pdf:
                generar_pdf_informe(informe)
            
            subject = f'Informe de Mantenimiento - Solicitud #{informe.codigo_solicitud.codigo_solicitud}'
            message = f"""Estimado cliente,

Adjunto encontrará el informe de mantenimiento solicitado.

Detalles:
- Solicitud: #{informe.codigo_solicitud.codigo_solicitud}
- Máquina: {informe.codigo_maquinaria.marca} {informe.codigo_maquinaria.modelo}
- Fecha: {informe.fecha_informe.strftime('%d/%m/%Y %H:%M')}
- Descripción: {informe.descripcion[:200]}...

Saludos cordiales,
Sistema MantenTask
            """
            
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario],
            )
            
            # Adjuntar el PDF
            if informe.archivo_pdf:
                email.attach_file(informe.archivo_pdf.path)
            
            email.send(fail_silently=False)
            
            logger.info(f"Informe #{informe.codigo_solicitud.codigo_solicitud} enviado a {destinatario}")
            
            return Response({
                'mensaje': 'Correo enviado exitosamente',
                'destinatario': destinatario,
                'adjunto': bool(informe.archivo_pdf)
            })
        except Exception as e:
            logger.error(f"Error al enviar correo con informe: {str(e)}")
            return Response(
                {'error': f'Error al enviar correo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ViewSet legacy para compatibilidad
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

# Admin Dashboard ViewSet
class AdminDashboardViewSet(viewsets.ViewSet):
    """Endpoints para el panel de administración"""
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas generales del sistema"""
        return Response({
            'total_usuarios': Usuario.objects.count(),
            'total_solicitudes': Solicitud.objects.count(),
            'total_maquinas': Maquina.objects.count(),
            'total_sucursales': Sucursal.objects.count(),
            'solicitudes_pendientes': Solicitud.objects.filter(codigo_estado=1).count(),
            'solicitudes_en_proceso': Solicitud.objects.filter(codigo_estado=2).count(),
            'solicitudes_completadas': Solicitud.objects.filter(codigo_estado=3).count(),
        })
    
    @action(detail=False, methods=['get'])
    def usuarios_dashboard(self, request):
        """Listar todos los usuarios para el admin"""
        usuarios = Usuario.objects.all().values(
            'id_usuario', 'username', 'first_name', 'apellido_paterno', 'apellido_materno',
            'correo_electronico', 'codigo_tipo_usuario', 'codigo_nivel_acceso', 'is_active', 'date_joined'
        )
        return Response(list(usuarios))
    
    @action(detail=False, methods=['get'])
    def solicitudes_dashboard(self, request):
        """Listar todas las solicitudes para el admin con detalles"""
        solicitudes = Solicitud.objects.select_related(
            'codigo_maquinaria', 'id_usuario', 'codigo_estado'
        ).values(
            'codigo_solicitud', 'descripcion', 'fecha_creacion', 'fecha_actualizacion',
            'codigo_estado__nombre_estado', 'id_usuario__username', 
            'codigo_maquinaria__marca', 'codigo_maquinaria__modelo'
        ).order_by('-fecha_creacion')
        return Response(list(solicitudes))
    
    @action(detail=False, methods=['post'], url_path='cambiar-nivel-usuario/(?P<usuario_id>[^/.]+)')
    def cambiar_nivel_usuario(self, request, usuario_id=None):
        """
        Cambiar nivel de acceso de un usuario
        Solo administradores (codigo_nivel_acceso=4) pueden hacerlo
        No se puede cambiar el propio nivel
        """
        try:
            # Validar que sea admin
            if request.user.codigo_nivel_acceso != 4:
                return Response(
                    {'error': 'Solo administradores pueden cambiar niveles de acceso'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            nuevo_nivel = request.data.get('codigo_nivel_acceso')
            
            # No permitir cambiar el propio nivel
            if request.user.id_usuario == usuario.id_usuario:
                return Response(
                    {'error': 'No puedes cambiar tu propio nivel de acceso'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar nivel (1=Básico, 2=Intermedio, 3=Avanzado, 4=Administrador)
            if nuevo_nivel not in [1, 2, 3, 4]:
                return Response(
                    {'error': 'Nivel de acceso inválido. Debe ser 1, 2, 3 o 4'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            nivel_anterior = usuario.codigo_nivel_acceso
            usuario.codigo_nivel_acceso = nuevo_nivel
            usuario.save()
            
            # Registrar en logs
            logger.info(
                f"[ADMIN LOG] Usuario {request.user.username} cambió nivel de {usuario.username} "
                f"de {nivel_anterior} a {nuevo_nivel}"
            )
            
            return Response({
                'mensaje': f'Nivel de acceso actualizado a {usuario.get_codigo_nivel_acceso_display()}',
                'usuario_id': usuario.id_usuario,
                'usuario_username': usuario.username,
                'nivel_anterior': nivel_anterior,
                'nuevo_nivel': nuevo_nivel
            })
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], url_path='cambiar-tipo-usuario/(?P<usuario_id>[^/.]+)')
    def cambiar_tipo_usuario(self, request, usuario_id=None):
        """
        Cambiar tipo de usuario (Ingeniero/Encargado)
        Solo administradores (codigo_nivel_acceso=4) pueden hacerlo
        """
        try:
            # Validar que sea admin
            if request.user.codigo_nivel_acceso != 4:
                return Response(
                    {'error': 'Solo administradores pueden cambiar tipos de usuario'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            nuevo_tipo = request.data.get('codigo_tipo_usuario')
            
            # Validar tipo (1=Ingeniero, 2=Encargado)
            if nuevo_tipo not in [1, 2]:
                return Response(
                    {'error': 'Tipo de usuario inválido. Debe ser 1 (Ingeniero) o 2 (Encargado)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            tipo_anterior = usuario.codigo_tipo_usuario
            usuario.codigo_tipo_usuario = nuevo_tipo
            usuario.save()
            
            # Registrar en logs
            logger.info(
                f"[ADMIN LOG] Usuario {request.user.username} cambió tipo de {usuario.username} "
                f"de {tipo_anterior} a {nuevo_tipo}"
            )
            
            return Response({
                'mensaje': f'Tipo de usuario actualizado a {usuario.get_codigo_tipo_usuario_display()}',
                'usuario_id': usuario.id_usuario,
                'usuario_username': usuario.username,
                'tipo_anterior': tipo_anterior,
                'nuevo_tipo': nuevo_tipo
            })
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error al cambiar tipo de usuario: {str(e)}")
            return Response(
                {'error': f'Error al cambiar tipo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='desactivar-usuario/(?P<usuario_id>[^/.]+)')
    def desactivar_usuario(self, request, usuario_id=None):
        """Desactivar/Activar un usuario"""
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            usuario.is_active = not usuario.is_active
            usuario.save()
            
            estado = 'activado' if usuario.is_active else 'desactivado'
            return Response({
                'mensaje': f'Usuario {estado} exitosamente',
                'usuario_id': usuario.id_usuario,
                'is_active': usuario.is_active
            })
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )