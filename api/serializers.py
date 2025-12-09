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
            'apellido_materno', 'correo_electronico', 'password', 'contrasena',
            'codigo_sucursal', 'sucursal', 'codigo_tipo_usuario', 
            'tipo_usuario_nombre', 'codigo_nivel_acceso', 'nivel_acceso_nombre',
            'nombre_completo', 'is_active', 'date_joined'
        ]
        extra_kwargs = {
            'contrasena': {'write_only': True},
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
            usuario.contrasena = usuario.password  # Sincronizar campo legacy
        usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.contrasena = instance.password
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
            'modelo', 'marca', 'fecha_compra', 'fecha_instalacion', 
            'fecha_ultima_mantencion'
        ]


class MaquinaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para relaciones"""
    class Meta:
        model = Maquina
        fields = ['codigo_maquinaria', 'modelo', 'marca']


class SolicitudSerializer(serializers.ModelSerializer):
    maquina = MaquinaSimpleSerializer(source='codigo_maquinaria', read_only=True)
    usuario = UsuarioSimpleSerializer(source='id_usuario', read_only=True)
    estado = EstadoSerializer(source='codigo_estado', read_only=True)
    tiene_informe = serializers.SerializerMethodField()
    
    class Meta:
        model = Solicitud
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'maquina',
            'id_usuario', 'usuario', 'descripcion', 
            'codigo_estado', 'estado', 'fecha_creacion', 
            'fecha_actualizacion', 'tiene_informe'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_tiene_informe(self, obj):
        return hasattr(obj, 'informe')


class SolicitudCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar solicitudes"""
    class Meta:
        model = Solicitud
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 
            'descripcion', 'codigo_estado'
        ]
        read_only_fields = ['codigo_solicitud']


class InformeSerializer(serializers.ModelSerializer):
    solicitud = SolicitudSerializer(source='codigo_solicitud', read_only=True)
    maquina = MaquinaSimpleSerializer(source='codigo_maquinaria', read_only=True)
    usuario = UsuarioSimpleSerializer(source='id_usuario', read_only=True)
    archivo_pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Informe
        fields = [
            'codigo_solicitud', 'solicitud', 'codigo_maquinaria', 
            'maquina', 'id_usuario', 'usuario', 'descripcion', 
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
    class Meta:
        model = Informe
        fields = [
            'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 
            'descripcion', 'archivo_pdf'
        ]


# Serializer legacy para compatibilidad
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at']
