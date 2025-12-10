# Prueba: Enviar Informe por Correo con PDF Adjunto

## Resumen del problema y solución

**Problema:** El endpoint `enviar_por_correo` enviaba el correo pero NO adjuntaba el PDF.

**Solución:** Se implementó `EmailMessage` de Django que permite adjuntar archivos, reemplazando `send_mail()`.

## Pasos para probar

### 1. Asegúrate de tener datos en la base de datos

```bash
python manage.py create_test_data
```

O crea manualmente:
- Una máquina (GET `/api/maquinas/`)
- Una solicitud (GET `/api/solicitudes/`)
- Un informe (GET `/api/informes/`)

### 2. Configura credenciales SMTP en `.env`

Ejemplo con Gmail:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### 3. Prueba con Postman

**URL:** `POST http://127.0.0.1:8000/api/informes/1/enviar_por_correo/`

**Body (raw JSON):**
```json
{
  "email": "tu-email-destino@gmail.com"
}
```

### 4. Esperado

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Correo enviado exitosamente",
  "destinatario": "tu-email-destino@gmail.com",
  "adjunto": true
}
```

**En tu email deberías recibir:**
- Asunto: `Informe de Mantenimiento - Solicitud #1`
- Mensaje con detalles del informe
- **Archivo PDF adjunto** con nombre como: `informe_solicitud_1_20251210_164000.pdf`

## ¿Qué cambió?

| Antes | Después |
|-------|---------|
| `send_mail()` sin adjuntos | `EmailMessage()` con adjuntos |
| Solo texto del email | Texto + PDF como attachment |
| No había log de éxito/error | Log con `logger.info/error` |
| Respuesta genérica | Respuesta con detalles (`adjunto: true`) |

## Si el PDF no se adjunta

**Causas posibles:**

1. **El PDF no fue generado:** Verifica que `informe.archivo_pdf` NO esté vacío
   - Solución: Llama primero a `GET /api/informes/1/descargar_pdf/` para generar el PDF

2. **La ruta del archivo no existe:** `informe.archivo_pdf.path` falla
   - Solución: Verifica que la carpeta `/media/informes/` existe en el proyecto

3. **Configuración de MEDIA_ROOT:** Asegúrate que en `settings.py` está configurado
   ```python
   MEDIA_ROOT = base_dir / 'media'
   MEDIA_URL = '/media/'
   ```

## Verificar archivos generados

Los PDFs se guardan en: `H:\Mantentask\media\informes\`

Ejemplo:
```
media/
└── informes/
    ├── informe_solicitud_1_20251210_164000.pdf
    └── informe_solicitud_2_20251210_164530.pdf
```

## Monitoreo

Revisa los logs en `django.log` para confirmar el envío:

```
INFO ... api.views Informe #1 enviado a tu-email@gmail.com
```

## Troubleshooting

### Error: "SMTPAuthenticationError"
- Revisa credenciales en `.env`
- Si usas Gmail: asegúrate de usar "App Password", no contraseña normal

### Error: "ConnectionRefusedError"
- Verifica que el servidor SMTP está disponible
- Intenta con `python manage.py test_email --email tu-email@gmail.com`

### PDF vacío o corrupto
- El PDF se generó pero está malformado
- Solución: Llama a `POST /api/informes/1/regenerar_pdf/` para regenerar
