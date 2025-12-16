from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator


class Usuario(AbstractUser):
    """Modelo extendido de Usuario con roles y datos adicionales"""
    TIPO_USUARIO_CHOICES = [
        (1, 'Ingeniero'),
        (2, 'Encargado'),
    ]
    
    NIVEL_ACCESO_CHOICES = [
        (1, 'Básico'),
        (2, 'Intermedio'),
        (3, 'Avanzado'),
        (4, 'Administrador'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True, validators=[EmailValidator()])
    telefono = models.CharField(max_length=20, blank=True, null=True)
    contrasena = models.CharField(max_length=128)  # Django maneja el hash automáticamente
    codigo_sucursal = models.ForeignKey('Sucursal', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    codigo_tipo_usuario = models.IntegerField(choices=TIPO_USUARIO_CHOICES)
    codigo_nivel_acceso = models.IntegerField(choices=NIVEL_ACCESO_CHOICES)
    
    # Campos heredados de AbstractUser que usaremos
    # username, first_name, last_name, email, password, is_active, date_joined
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.apellido_paterno} {self.apellido_materno}"


class TipoUsuario(models.Model):
    """Catálogo de tipos de usuario"""
    codigo_tipo_usuario = models.AutoField(primary_key=True)
    nombre_tipo_usuario = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'tipo_usuario'
        verbose_name = 'Tipo de Usuario'
        verbose_name_plural = 'Tipos de Usuario'
    
    def __str__(self):
        return self.nombre_tipo_usuario


class NivelAcceso(models.Model):
    """Catálogo de niveles de acceso"""
    codigo_nivel_acceso = models.AutoField(primary_key=True)
    nombre_nivel_acceso = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'nivel_acceso'
        verbose_name = 'Nivel de Acceso'
        verbose_name_plural = 'Niveles de Acceso'
    
    def __str__(self):
        return self.nombre_nivel_acceso


class Sucursal(models.Model):
    """Sucursales de la organización"""
    codigo_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'sucursal'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
    
    def __str__(self):
        return self.nombre_sucursal


class Estado(models.Model):
    """Estados de las solicitudes"""
    codigo_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'estado'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
    
    def __str__(self):
        return self.nombre_estado


class Maquina(models.Model):
    """Máquinas/Equipos del sistema"""
    codigo_maquinaria = models.AutoField(primary_key=True)
    codigo_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='maquinas')
    modelo = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, null=True, blank=True)
    fecha_compra = models.DateField()
    fecha_instalacion = models.DateField()
    fecha_ultima_mantencion = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'maquina'
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.codigo_sucursal}"


class Solicitud(models.Model):
    """Solicitudes de mantenimiento (Tickets)"""
    codigo_solicitud = models.AutoField(primary_key=True)
    codigo_maquinaria = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='solicitudes')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes')
    descripcion = models.TextField()
    # Fecha opcional indicada por el usuario (por ejemplo, fecha solicitada/programada)
    fecha_programada = models.DateField(null=True, blank=True)
    codigo_estado = models.ForeignKey(Estado, on_delete=models.SET_DEFAULT, default=1, related_name='solicitudes')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Solicitud #{self.codigo_solicitud} - {self.codigo_maquinaria}"


class Informe(models.Model):
    """Informes generados a partir de solicitudes"""
    codigo_solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, primary_key=True, related_name='informe')
    codigo_maquinaria = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='informes')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='informes')
    descripcion = models.TextField()
    descripcion_trabajo = models.TextField(null=True, blank=True)
    piezas_reemplazadas = models.TextField(null=True, blank=True)
    recomendaciones = models.TextField(null=True, blank=True)
    fecha_informe = models.DateTimeField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='informes/', null=True, blank=True)
    
    class Meta:
        db_table = 'informe'
        verbose_name = 'Informe'
        verbose_name_plural = 'Informes'
    
    def __str__(self):
        return f"Informe - Solicitud #{self.codigo_solicitud.codigo_solicitud}"


# Modelo legacy para compatibilidad
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
