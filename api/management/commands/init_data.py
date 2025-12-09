"""
Script para inicializar datos básicos del sistema MantenTask
"""
from django.core.management.base import BaseCommand
from api.models import TipoUsuario, NivelAcceso, Estado


class Command(BaseCommand):
    help = 'Inicializa datos básicos del sistema (tipos de usuario, niveles de acceso, estados)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Inicializando datos básicos...')
        
        # Crear tipos de usuario
        tipos_usuario = [
            {'codigo': 1, 'nombre': 'Ingeniero'},
            {'codigo': 2, 'nombre': 'Encargado'},
        ]
        
        for tipo in tipos_usuario:
            obj, created = TipoUsuario.objects.get_or_create(
                codigo_tipo_usuario=tipo['codigo'],
                defaults={'nombre_tipo_usuario': tipo['nombre']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Tipo de usuario creado: {tipo["nombre"]}'))
            else:
                self.stdout.write(f'  Tipo de usuario ya existe: {tipo["nombre"]}')
        
        # Crear niveles de acceso
        niveles_acceso = [
            {'codigo': 1, 'nombre': 'Básico'},
            {'codigo': 2, 'nombre': 'Intermedio'},
            {'codigo': 3, 'nombre': 'Avanzado'},
            {'codigo': 4, 'nombre': 'Administrador'},
        ]
        
        for nivel in niveles_acceso:
            obj, created = NivelAcceso.objects.get_or_create(
                codigo_nivel_acceso=nivel['codigo'],
                defaults={'nombre_nivel_acceso': nivel['nombre']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Nivel de acceso creado: {nivel["nombre"]}'))
            else:
                self.stdout.write(f'  Nivel de acceso ya existe: {nivel["nombre"]}')
        
        # Crear estados
        estados = [
            {'codigo': 1, 'nombre': 'Pendiente'},
            {'codigo': 2, 'nombre': 'En Proceso'},
            {'codigo': 3, 'nombre': 'Completado'},
            {'codigo': 4, 'nombre': 'Cancelado'},
        ]
        
        for estado in estados:
            obj, created = Estado.objects.get_or_create(
                codigo_estado=estado['codigo'],
                defaults={'nombre_estado': estado['nombre']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Estado creado: {estado["nombre"]}'))
            else:
                self.stdout.write(f'  Estado ya existe: {estado["nombre"]}')
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos básicos inicializados correctamente!'))
