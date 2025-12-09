"""
Script para crear datos de prueba en el sistema MantenTask
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import (
    Usuario, Sucursal, Maquina, Solicitud, Informe,
    TipoUsuario, NivelAcceso, Estado
)


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema MantenTask'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creando datos de prueba...\n')
        
        # Crear sucursales
        self.stdout.write('Creando sucursales...')
        sucursales = [
            Sucursal.objects.create(nombre_sucursal='Sucursal Centro'),
            Sucursal.objects.create(nombre_sucursal='Sucursal Norte'),
            Sucursal.objects.create(nombre_sucursal='Sucursal Sur'),
        ]
        self.stdout.write(self.style.SUCCESS(f'✓ {len(sucursales)} sucursales creadas'))
        
        # Crear usuarios de prueba
        self.stdout.write('\nCreando usuarios...')
        
        # Superusuario/Administrador
        admin = Usuario.objects.create_superuser(
            username='admin',
            first_name='Admin',
            apellido_paterno='Sistema',
            apellido_materno='MantenTask',
            correo_electronico='admin@mantentask.com',
            password='admin123',
            codigo_tipo_usuario=1,
            codigo_nivel_acceso=4,
            codigo_sucursal=sucursales[0]
        )
        self.stdout.write(self.style.SUCCESS('✓ Superusuario creado: admin / admin123'))
        
        # Ingenieros
        ingeniero1 = Usuario.objects.create_user(
            username='jperez',
            first_name='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            correo_electronico='juan.perez@mantentask.com',
            password='ingeniero123',
            codigo_tipo_usuario=1,  # Ingeniero
            codigo_nivel_acceso=3,
            codigo_sucursal=sucursales[0]
        )
        
        ingeniero2 = Usuario.objects.create_user(
            username='mlopez',
            first_name='María',
            apellido_paterno='López',
            apellido_materno='Sánchez',
            correo_electronico='maria.lopez@mantentask.com',
            password='ingeniero123',
            codigo_tipo_usuario=1,
            codigo_nivel_acceso=3,
            codigo_sucursal=sucursales[1]
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Ingenieros creados: jperez, mlopez / ingeniero123'))
        
        # Encargados
        encargado1 = Usuario.objects.create_user(
            username='crodriguez',
            first_name='Carlos',
            apellido_paterno='Rodríguez',
            apellido_materno='Martínez',
            correo_electronico='carlos.rodriguez@mantentask.com',
            password='encargado123',
            codigo_tipo_usuario=2,  # Encargado
            codigo_nivel_acceso=2,
            codigo_sucursal=sucursales[0]
        )
        
        encargado2 = Usuario.objects.create_user(
            username='agarcia',
            first_name='Ana',
            apellido_paterno='García',
            apellido_materno='Torres',
            correo_electronico='ana.garcia@mantentask.com',
            password='encargado123',
            codigo_tipo_usuario=2,
            codigo_nivel_acceso=2,
            codigo_sucursal=sucursales[2]
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Encargados creados: crodriguez, agarcia / encargado123'))
        
        # Crear máquinas
        self.stdout.write('\nCreando máquinas...')
        maquinas = [
            Maquina.objects.create(
                codigo_sucursal=sucursales[0],
                modelo='Industrial XL-2000',
                marca='Siemens',
                fecha_compra=timezone.now().date() - timedelta(days=365),
                fecha_instalacion=timezone.now().date() - timedelta(days=350)
            ),
            Maquina.objects.create(
                codigo_sucursal=sucursales[0],
                modelo='Compresor Pro 5000',
                marca='Atlas Copco',
                fecha_compra=timezone.now().date() - timedelta(days=730),
                fecha_instalacion=timezone.now().date() - timedelta(days=720),
                fecha_ultima_mantencion=timezone.now().date() - timedelta(days=30)
            ),
            Maquina.objects.create(
                codigo_sucursal=sucursales[1],
                modelo='Torno CNC TX-300',
                marca='Haas',
                fecha_compra=timezone.now().date() - timedelta(days=180),
                fecha_instalacion=timezone.now().date() - timedelta(days=170)
            ),
            Maquina.objects.create(
                codigo_sucursal=sucursales[1],
                modelo='Soldadora MIG 250',
                marca='Lincoln Electric',
                fecha_compra=timezone.now().date() - timedelta(days=90),
                fecha_instalacion=timezone.now().date() - timedelta(days=85)
            ),
            Maquina.objects.create(
                codigo_sucursal=sucursales[2],
                modelo='Prensa Hidráulica PH-100',
                marca='Schuler',
                fecha_compra=timezone.now().date() - timedelta(days=500),
                fecha_instalacion=timezone.now().date() - timedelta(days=490),
                fecha_ultima_mantencion=timezone.now().date() - timedelta(days=60)
            ),
        ]
        self.stdout.write(self.style.SUCCESS(f'✓ {len(maquinas)} máquinas creadas'))
        
        # Obtener estados
        estado_pendiente = Estado.objects.get(codigo_estado=1)
        estado_proceso = Estado.objects.get(codigo_estado=2)
        estado_completado = Estado.objects.get(codigo_estado=3)
        
        # Crear solicitudes
        self.stdout.write('\nCreando solicitudes...')
        
        solicitud1 = Solicitud.objects.create(
            codigo_maquinaria=maquinas[0],
            id_usuario=encargado1,
            descripcion='La máquina presenta ruidos extraños y vibración excesiva durante el funcionamiento.',
            codigo_estado=estado_proceso,
            fecha_creacion=timezone.now() - timedelta(days=5)
        )
        
        solicitud2 = Solicitud.objects.create(
            codigo_maquinaria=maquinas[1],
            id_usuario=encargado1,
            descripcion='El compresor no alcanza la presión requerida. Se necesita revisión urgente.',
            codigo_estado=estado_pendiente,
            fecha_creacion=timezone.now() - timedelta(days=2)
        )
        
        solicitud3 = Solicitud.objects.create(
            codigo_maquinaria=maquinas[2],
            id_usuario=encargado2,
            descripcion='El torno CNC muestra errores en el control numérico. Pantalla parpadeante.',
            codigo_estado=estado_completado,
            fecha_creacion=timezone.now() - timedelta(days=10)
        )
        
        solicitud4 = Solicitud.objects.create(
            codigo_maquinaria=maquinas[3],
            id_usuario=ingeniero2,
            descripcion='Mantenimiento preventivo programado. Revisión general de componentes.',
            codigo_estado=estado_proceso,
            fecha_creacion=timezone.now() - timedelta(days=1)
        )
        
        solicitud5 = Solicitud.objects.create(
            codigo_maquinaria=maquinas[4],
            id_usuario=encargado2,
            descripcion='Fuga de aceite hidráulico en el sistema principal. Producción detenida.',
            codigo_estado=estado_completado,
            fecha_creacion=timezone.now() - timedelta(days=15)
        )
        
        self.stdout.write(self.style.SUCCESS('✓ 5 solicitudes creadas'))
        
        # Crear informes para solicitudes completadas
        self.stdout.write('\nCreando informes...')
        
        informe1 = Informe.objects.create(
            codigo_solicitud=solicitud3,
            codigo_maquinaria=solicitud3.codigo_maquinaria,
            id_usuario=ingeniero2,
            descripcion='''Se realizó diagnóstico completo del sistema de control numérico.
            
Trabajo realizado:
- Actualización de firmware del controlador
- Reemplazo de cable de pantalla defectuoso
- Calibración de ejes X, Y, Z
- Pruebas de funcionamiento exitosas

La máquina está operativa y funcionando correctamente.''',
            fecha_informe=timezone.now() - timedelta(days=8)
        )
        
        informe2 = Informe.objects.create(
            codigo_solicitud=solicitud5,
            codigo_maquinaria=solicitud5.codigo_maquinaria,
            id_usuario=ingeniero1,
            descripcion='''Se atendió la emergencia de fuga de aceite hidráulico.

Trabajo realizado:
- Identificación de sello defectuoso en cilindro principal
- Reemplazo de sello hidráulico
- Recarga del sistema hidráulico con aceite especificado
- Pruebas de presión satisfactorias
- Limpieza del área de trabajo

La prensa está operativa. Se recomienda monitoreo durante las próximas 48 horas.''',
            fecha_informe=timezone.now() - timedelta(days=14)
        )
        
        self.stdout.write(self.style.SUCCESS('✓ 2 informes creados'))
        
        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('¡Datos de prueba creados exitosamente!'))
        self.stdout.write('='*60)
        self.stdout.write('\nCredenciales de acceso:')
        self.stdout.write('  Admin:      admin / admin123')
        self.stdout.write('  Ingenieros: jperez, mlopez / ingeniero123')
        self.stdout.write('  Encargados: crodriguez, agarcia / encargado123')
        self.stdout.write('\nAccede al panel de administración:')
        self.stdout.write('  http://127.0.0.1:8000/admin/')
        self.stdout.write('\nAccede a la API REST:')
        self.stdout.write('  http://127.0.0.1:8000/api/')
        self.stdout.write('\nDatos creados:')
        self.stdout.write(f'  • {Sucursal.objects.count()} sucursales')
        self.stdout.write(f'  • {Usuario.objects.count()} usuarios')
        self.stdout.write(f'  • {Maquina.objects.count()} máquinas')
        self.stdout.write(f'  • {Solicitud.objects.count()} solicitudes')
        self.stdout.write(f'  • {Informe.objects.count()} informes')
        self.stdout.write('='*60 + '\n')
