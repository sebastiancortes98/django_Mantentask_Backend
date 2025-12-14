"""
Script para inicializar datos básicos del sistema MantenTask
"""
from django.core.management.base import BaseCommand
from api.models import TipoUsuario, NivelAcceso, Estado, Sucursal, Usuario, Maquina
from datetime import date, timedelta


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
        
        # Crear sucursales
        sucursales = [
            {'codigo': 1, 'nombre': 'Sucursal Principal'},
            {'codigo': 2, 'nombre': 'Sucursal Norte'},
            {'codigo': 3, 'nombre': 'Sucursal Sur'},
        ]
        
        for suc in sucursales:
            obj, created = Sucursal.objects.get_or_create(
                codigo_sucursal=suc['codigo'],
                defaults={'nombre_sucursal': suc['nombre']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Sucursal creada: {suc["nombre"]}'))
            else:
                self.stdout.write(f'  Sucursal ya existe: {suc["nombre"]}')
        
        # Crear usuario administrador por defecto
        sucursal_principal = Sucursal.objects.get(codigo_sucursal=1)
        if not Usuario.objects.filter(username='admin').exists():
            admin = Usuario.objects.create_user(
                username='admin',
                password='admin123',
                first_name='Administrador',
                apellido_paterno='Sistema',
                apellido_materno='MantenTask',
                correo_electronico='admin@mantentask.com',
                codigo_tipo_usuario=2,  # Encargado
                codigo_nivel_acceso=4,  # Administrador
                codigo_sucursal=sucursal_principal,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Usuario administrador creado: admin/admin123'))
        else:
            self.stdout.write('  Usuario administrador ya existe')
        
        # Crear máquinas de ejemplo
        maquinas = [
            {
                'sucursal': 1,
                'modelo': 'Compresor Industrial Pro 3000',
                'marca': 'Atlas Copco',
                'fecha_compra': date.today() - timedelta(days=730),
                'fecha_instalacion': date.today() - timedelta(days=720),
            },
            {
                'sucursal': 1,
                'modelo': 'Torno CNC T-450',
                'marca': 'Haas',
                'fecha_compra': date.today() - timedelta(days=365),
                'fecha_instalacion': date.today() - timedelta(days=355),
            },
            {
                'sucursal': 2,
                'modelo': 'Montacargas EFG 2.0',
                'marca': 'Jungheinrich',
                'fecha_compra': date.today() - timedelta(days=500),
                'fecha_instalacion': date.today() - timedelta(days=490),
            },
            {
                'sucursal': 2,
                'modelo': 'Generador Diesel 150kW',
                'marca': 'Caterpillar',
                'fecha_compra': date.today() - timedelta(days=1000),
                'fecha_instalacion': date.today() - timedelta(days=990),
            },
            {
                'sucursal': 3,
                'modelo': 'Bomba Centrífuga HC-500',
                'marca': 'Grundfos',
                'fecha_compra': date.today() - timedelta(days=600),
                'fecha_instalacion': date.today() - timedelta(days=590),
            },
        ]
        
        for maq in maquinas:
            sucursal = Sucursal.objects.get(codigo_sucursal=maq['sucursal'])
            obj, created = Maquina.objects.get_or_create(
                modelo=maq['modelo'],
                marca=maq['marca'],
                defaults={
                    'codigo_sucursal': sucursal,
                    'fecha_compra': maq['fecha_compra'],
                    'fecha_instalacion': maq['fecha_instalacion'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Máquina creada: {maq["marca"]} {maq["modelo"]}'))
            else:
                self.stdout.write(f'  Máquina ya existe: {maq["marca"]} {maq["modelo"]}')
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos básicos inicializados correctamente!'))
