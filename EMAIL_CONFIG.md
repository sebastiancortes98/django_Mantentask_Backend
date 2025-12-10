# CONFIGURACIÓN DE CORREO ELECTRÓNICO

## Pasos para configurar el servicio de email real

### 1. Opción A: Gmail (Recomendado para desarrollo)

#### 1.1 Habilitar "Contraseñas de aplicación"
- Accede a https://myaccount.google.com/security
- En el menú izquierdo, selecciona "Seguridad"
- Baja hasta "Contraseñas de aplicación"
- Selecciona "Correo" y "Windows (o tu OS)"
- Google te generará una contraseña de 16 caracteres

#### 1.2 Configurar en `.env`
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### 2. Opción B: Outlook / Office365

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@outlook.com
EMAIL_HOST_PASSWORD=tu-contraseña-normal
DEFAULT_FROM_EMAIL=tu-email@outlook.com
```

### 3. Opción C: Servidor SMTP personalizado

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.tuservidor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=usuario@tuservidor.com
EMAIL_HOST_PASSWORD=tu-contraseña
DEFAULT_FROM_EMAIL=mantentask@tudominio.com
```

### 4. Opción D: Consola (solo desarrollo, no envía realmente)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Prueba la configuración

Una vez configurado, prueba con el comando:

```bash
python manage.py test_email --email tu-email-prueba@gmail.com
```

### Salida esperada en caso de éxito:
```
✓ ¡Correo enviado exitosamente!
  Destinatario: tu-email@gmail.com
  Asunto: Prueba de Correo - MantenTask
```

## Errores comunes

### "SMTPAuthenticationError: Application-specific password required"
- **Solución:** Usando Gmail, genera una "Contraseña de aplicación" en vez de la contraseña normal
- https://myaccount.google.com/apppasswords

### "SMTPException: SMTP AUTH extension not supported by server"
- **Solución:** Verifica el puerto (587 para TLS, 465 para SSL)

### "SMTPServerDisconnected: Connection unexpectedly closed"
- **Solución:** El servidor rechazó la conexión; verifica credenciales y puerto

### "No module named 'smtplib'"
- **Solución:** Raramente ocurre; reinstala Python o verifica la instalación

## Notificaciones automáticas

Con email configurado, el sistema envía automáticamente:

1. **Nueva solicitud creada** → Notificación a todos los ingenieros activos
2. **Cambio de estado** → Notificación al usuario que creó la solicitud
3. **Envío manual de informe** → Via endpoint `/api/informes/{id}/enviar_por_correo/`

Ejemplo para enviar informe por correo:
```bash
POST /api/informes/1/enviar_por_correo/
Body: { "email": "destinatario@empresa.com" }
```

## Monitoreo de errores

Los errores de envío de email se registran en `django.log` y en la consola. No interrumpen el flujo de la solicitud.

Para revisar los logs:
```bash
tail -f django.log  # Linux/Mac
Get-Content django.log -Tail 20 -Wait  # PowerShell
```
