"""
Script para probar la configuración de correo electrónico
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prueba la configuración de correo electrónico del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de prueba a enviar (ej: tu-email@gmail.com)',
            required=True
        )

    def handle(self, *args, **options):
        email_destino = options['email']
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PRUEBA DE CORREO ELECTRÓNICO'))
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write('Configuración actual:')
        self.stdout.write(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'\n  Email de prueba: {email_destino}\n')
        
        try:
            subject = 'Prueba de Correo - MantenTask'
            message = '''
Hola,

Este es un correo de prueba del sistema MantenTask.

Si recibiste este mensaje, significa que la configuración de correo electrónico está funcionando correctamente.

Saludos,
Sistema MantenTask
            '''
            
            self.stdout.write('Intentando enviar correo...')
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email_destino],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('\n✓ ¡Correo enviado exitosamente!'))
            self.stdout.write(f'  Destinatario: {email_destino}')
            self.stdout.write(f'  Asunto: {subject}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR('\n✗ Error al enviar correo:'))
            self.stdout.write(self.style.ERROR(f'  {str(e)}'))
            self.stdout.write('\nVerifica:')
            self.stdout.write('  1. Las credenciales en .env son correctas')
            self.stdout.write('  2. Si usas Gmail: habilita "Contraseñas de aplicación"')
            self.stdout.write('  3. Si usas Outlook: verifica el puerto (587 para SMTP)')
            self.stdout.write('  4. Revisa el archivo django.log para más detalles')
            
        self.stdout.write('\n' + '='*60 + '\n')
