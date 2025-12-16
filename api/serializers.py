from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    Usuario, TipoUsuario, NivelAcceso, Sucursal, 
    Estado, Maquina, Solicitud, Informe, Task
)


class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['codigo_tipo_usuario', 'nombre_tipo_usuario']


class NivelAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelAcceso
        fields = ['codigo_nivel_acceso', 'nombre_nivel_acceso']


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = ['codigo_sucursal', 'nombre_sucursal']


class UsuarioSerializer(serializers.ModelSerializer):
    sucursal = SucursalSerializer(source='codigo_sucursal', read_only=True)
    tipo_usuario_nombre = serializers.CharField(source='get_codigo_tipo_usuario_display', read_only=True)
    nivel_acceso_nombre = serializers.CharField(source='get_codigo_nivel_acceso_display', read_only=True)
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'username', 'first_name', 'apellido_paterno', 
            'apellido_materno', 'correo_electronico', 'telefono', 'password', 'contrasena',
            'codigo_sucursal', 'sucursal', 'codigo_tipo_usuario', 
            'tipo_usuario_nombre', 'codigo_nivel_acceso', 'nivel_acceso_nombre',
            'nombre_completo', 'is_active', 'date_joined'
        ]
        extra_kwargs = {
            'contrasena': {'write_only': True, 'required': False},
            'password': {'write_only': True, 'required': False},
            'codigo_tipo_usuario': {'required': False},  # Default al crear
            'codigo_nivel_acceso': {'required': False},  # Default al crear
            'codigo_sucursal': {'required': False},  # Opcional
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('contrasena', None)  # Ignorar si viene, Django lo maneja
        
        # Defaults para nuevos usuarios
        validated_data.setdefault('codigo_tipo_usuario', 1)  # Ingeniero
        validated_data.setdefault('codigo_nivel_acceso', 1)  # Básico
        
        usuario = Usuario.objects.create(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('contrasena', None)  # Ignorar si viene
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UsuarioSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para relaciones"""
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'username', 'nombre_completo', 'correo_electronico']


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['codigo_estado', 'nombre_estado']


class MaquinaSerializer(serializers.ModelSerializer):
    sucursal = SucursalSerializer(source='codigo_sucursal', read_only=True)
    
    class Meta:
        model = Maquina
        fields = [
            'codigo_maquinaria', 'codigo_sucursal', 'sucursal', 
            'modelo', 'marca', 'numero_serie', 'fecha_compra', 'fecha_instalacion', 
            'fecha_ultima_mantencion'
        ]


class MaquinaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para relaciones"""
    class Meta:
        model = Maquina
        fields = ['codigo_maquinaria', 'modelo', 'marca', 'numero_serie']


class SolicitudSerializer(serializers.ModelSerializer):
    maquina = MaquinaSimpleSerializer(source='codigo_maquinaria', read_only=True)
    usuario = UsuarioSimpleSerializer(source='id_usuario', read_only=True)
    ingeniero = UsuarioSimpleSerializer(source='ingeniero_asignado', read_only=True)
    estado = EstadoSerializer(source='codigo_estado', read_only=True)
    tiene_informe = serializers.SerializerMethodField()
    fecha_solicitud = serializers.SerializerMethodField()
    nombre_usuario = serializers.CharField(source='id_usuario.get_full_name', read_only=True)
    nombre_ingeniero = serializers.CharField(source='ingeniero_asignado.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Solicitud
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'maquina',
            'id_usuario', 'usuario', 'nombre_usuario', 
            'ingeniero_asignado', 'ingeniero', 'nombre_ingeniero',
            'descripcion', 
            'codigo_estado', 'estado', 'fecha_creacion', 'fecha_solicitud', 'fecha_programada',
            'fecha_actualizacion', 'tiene_informe'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_tiene_informe(self, obj):
        return hasattr(obj, 'informe')

    def get_fecha_solicitud(self, obj):
        # Alias para compatibilidad con el frontend
        return obj.fecha_creacion.date().isoformat() if obj.fecha_creacion else None


class SolicitudCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar solicitudes"""
    def validate(self, attrs):
        # Si no viene id_usuario, tomarlo del usuario autenticado (context)
        request = self.context.get('request')
        if not attrs.get('id_usuario') and request and request.user and request.user.is_authenticated:
            attrs['id_usuario'] = request.user
        # Si no viene codigo_estado, por defecto 1 (Pendiente)
        if not attrs.get('codigo_estado'):
            attrs['codigo_estado'] = 1
        return super().validate(attrs)

    def create(self, validated_data):
        # Refuerzo: si viene sin id_usuario, asignar request.user
        request = self.context.get('request')
        if not validated_data.get('id_usuario') and request and request.user and request.user.is_authenticated:
            validated_data['id_usuario'] = request.user
        if not validated_data.get('codigo_estado'):
            validated_data['codigo_estado'] = 1
        return super().create(validated_data)

    class Meta:
        model = Solicitud
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 
            'descripcion', 'fecha_programada', 'codigo_estado'
        ]
        read_only_fields = ['codigo_solicitud']
        extra_kwargs = {
            'id_usuario': {'required': False},
            'codigo_estado': {'required': False},
            'fecha_programada': {'required': False},
        }


class InformeSerializer(serializers.ModelSerializer):
    solicitud = SolicitudSerializer(source='codigo_solicitud', read_only=True)
    maquina = MaquinaSimpleSerializer(source='codigo_maquinaria', read_only=True)
    usuario = UsuarioSimpleSerializer(source='id_usuario', read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField()
    codigo_informe = serializers.IntegerField(source='codigo_solicitud_id', read_only=True)
    
    class Meta:
        model = Informe
        fields = [
            'codigo_informe', 'codigo_solicitud', 'solicitud', 'codigo_maquinaria', 
            'maquina', 'id_usuario', 'usuario', 'descripcion', 'descripcion_trabajo',
            'piezas_reemplazadas', 'recomendaciones',
            'fecha_informe', 'archivo_pdf', 'archivo_pdf_url'
        ]
        read_only_fields = ['fecha_informe']
    
    def get_archivo_pdf_url(self, obj):
        if obj.archivo_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_pdf.url)
        return None


class InformeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar informes"""
    def validate(self, attrs):
        request = self.context.get('request')
        if not attrs.get('id_usuario') and request and getattr(request.user, 'is_authenticated', False):
            attrs['id_usuario'] = request.user
        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('id_usuario') and request and getattr(request.user, 'is_authenticated', False):
            validated_data['id_usuario'] = request.user
        return super().create(validated_data)
    class Meta:
        model = Informe
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 
            'descripcion', 'descripcion_trabajo', 'piezas_reemplazadas', 'recomendaciones',
            'archivo_pdf'
        ]


# Serializer legacy para compatibilidad
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at']
