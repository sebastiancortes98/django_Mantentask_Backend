from django.contrib import admin
from .models import (
    Usuario, TipoUsuario, NivelAcceso, Sucursal,
    Estado, Maquina, Solicitud, Informe, Task
)


@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['codigo_tipo_usuario', 'nombre_tipo_usuario']
    search_fields = ['nombre_tipo_usuario']


@admin.register(NivelAcceso)
class NivelAccesoAdmin(admin.ModelAdmin):
    list_display = ['codigo_nivel_acceso', 'nombre_nivel_acceso']
    search_fields = ['nombre_nivel_acceso']


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ['codigo_sucursal', 'nombre_sucursal']
    search_fields = ['nombre_sucursal']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'id_usuario', 'username', 'first_name', 'apellido_paterno', 
        'correo_electronico', 'codigo_tipo_usuario', 'is_active'
    ]
    list_filter = ['codigo_tipo_usuario', 'codigo_nivel_acceso', 'is_active', 'codigo_sucursal']
    search_fields = ['username', 'first_name', 'apellido_paterno', 'apellido_materno', 'correo_electronico']
    ordering = ['-date_joined']


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['codigo_estado', 'nombre_estado']
    search_fields = ['nombre_estado']


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_maquinaria', 'marca', 'modelo', 'codigo_sucursal', 
        'fecha_compra', 'fecha_ultima_mantencion'
    ]
    list_filter = ['marca', 'codigo_sucursal']
    search_fields = ['marca', 'modelo']
    date_hierarchy = 'fecha_compra'


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 
        'codigo_estado', 'fecha_creacion', 'fecha_actualizacion'
    ]
    list_filter = ['codigo_estado', 'fecha_creacion']
    search_fields = ['descripcion', 'codigo_maquinaria__marca', 'codigo_maquinaria__modelo']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_solicitud', 'codigo_maquinaria', 'id_usuario', 'fecha_informe'
    ]
    list_filter = ['fecha_informe']
    search_fields = ['descripcion', 'codigo_maquinaria__marca']
    date_hierarchy = 'fecha_informe'
    readonly_fields = ['fecha_informe']


# Legacy
admin.site.register(Task)
