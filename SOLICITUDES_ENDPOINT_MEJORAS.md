# Mejoras en el Endpoint de Solicitudes

## Cambios Implementados

### 1. Optimización de Queries (N+1 Problem)

**Archivo:** `api/views.py` - `SolicitudViewSet`

Se agregó el método `get_queryset()` con `select_related()` para cargar relaciones en una sola query:

```python
def get_queryset(self):
    """Optimizar queries con select_related para evitar N+1"""
    return Solicitud.objects.select_related(
        'id_usuario',
        'codigo_maquinaria',
        'codigo_maquinaria__codigo_sucursal',
        'codigo_estado'
    )
```

**Beneficio:** Reduce las queries de N+1 a 1 query para listar todas las solicitudes con sus relaciones.

---

### 2. Campo `nombre_usuario` Directo

**Archivo:** `api/serializers.py` - `SolicitudSerializer`

Se agregó el campo `nombre_usuario` como alias directo del nombre completo del usuario:

```python
nombre_usuario = serializers.CharField(source='id_usuario.get_full_name', read_only=True)
```

**Incluido en fields:**
```python
fields = [
    'codigo_solicitud', 'codigo_maquinaria', 'maquina',
    'id_usuario', 'usuario', 'nombre_usuario', 'descripcion', 
    'codigo_estado', 'estado', 'fecha_creacion', 'fecha_solicitud', 'fecha_programada',
    'fecha_actualizacion', 'tiene_informe'
]
```

---

### 3. Campo `fecha_solicitud` (Ya implementado anteriormente)

**Archivo:** `api/serializers.py` - `SolicitudSerializer`

Se agregó `fecha_solicitud` como método que retorna `fecha_creacion` en formato de fecha:

```python
def get_fecha_solicitud(self, obj):
    # Alias para compatibilidad con el frontend
    return obj.fecha_creacion.date().isoformat() if obj.fecha_creacion else None
```

**Beneficio:** El frontend recibe la fecha en formato ISO simple (YYYY-MM-DD) sin el timestamp.

---

## Respuesta del Endpoint

### GET /api/solicitudes/

**Ejemplo de respuesta (cada item incluye):**

```json
{
  "codigo_solicitud": 1,
  "codigo_maquinaria": 3,
  "maquina": {
    "codigo_maquinaria": 3,
    "modelo": "Modelo X",
    "marca": "Marca Y",
    "numero_serie": "SN-12345"
  },
  "id_usuario": 5,
  "usuario": {
    "id_usuario": 5,
    "username": "jperez",
    "nombre_completo": "Juan Pérez García",
    "correo_electronico": "jperez@example.com"
  },
  "nombre_usuario": "Juan Pérez García",
  "descripcion": "Requiere mantenimiento preventivo",
  "codigo_estado": 1,
  "estado": {
    "codigo_estado": 1,
    "nombre_estado": "Pendiente"
  },
  "fecha_creacion": "2025-12-16T10:30:00Z",
  "fecha_solicitud": "2025-12-16",
  "fecha_programada": "2025-12-20",
  "fecha_actualizacion": "2025-12-16T10:30:00Z",
  "tiene_informe": false
}
```

---

## Campos Disponibles para el Frontend

### Para mostrar Usuario:
- **Opción 1:** `nombre_usuario` (string simple) → **"Juan Pérez García"**
- **Opción 2:** `usuario.nombre_completo` (objeto expandido) → **"Juan Pérez García"**
- **Opción 3:** `usuario.username` → **"jperez"**

### Para mostrar Fecha:
- **Opción 1:** `fecha_solicitud` (formato fecha ISO) → **"2025-12-16"**
- **Opción 2:** `fecha_creacion` (timestamp completo) → **"2025-12-16T10:30:00Z"**
- **Opción 3:** `fecha_programada` (si está disponible) → **"2025-12-20"**

---

## Funcionalidad Preservada

### POST /api/solicitudes/

**No hay cambios.** El endpoint sigue aceptando el mismo payload:

```json
{
  "codigo_maquinaria": 3,
  "descripcion": "Descripción del problema",
  "fecha_programada": "2025-12-20",
  "codigo_estado": 1
}
```

- Si `id_usuario` no se envía, se auto-completa con `request.user`
- Si `codigo_estado` no se envía, se usa `1` (Pendiente)

### PATCH /api/solicitudes/{id}/

**No hay cambios.** Sigue funcionando con actualizaciones parciales.

---

## Pruebas Recomendadas

### 1. Verificar que los campos aparecen en el listado:

```bash
# Con autenticación JWT
curl -H "Authorization: Bearer {token}" https://tu-api.com/api/solicitudes/
```

**Verificar que cada item incluya:**
- ✅ `nombre_usuario` con valor string
- ✅ `fecha_solicitud` con fecha ISO
- ✅ `usuario` expandido con `nombre_completo`
- ✅ `maquina` expandida con `numero_serie`

### 2. Verificar que POST funciona igual:

```bash
curl -X POST https://tu-api.com/api/solicitudes/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_maquinaria": 1,
    "descripcion": "Test"
  }'
```

**Verificar que:**
- ✅ Se crea la solicitud
- ✅ `id_usuario` se auto-completa
- ✅ `fecha_creacion` se genera automáticamente

### 3. Verificar que PATCH funciona igual:

```bash
curl -X PATCH https://tu-api.com/api/solicitudes/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_estado": 2
  }'
```

---

## Migración a Producción

### No requiere migraciones de base de datos

Todos los cambios son a nivel de serializers y viewsets. No se modificó el esquema de la base de datos.

### Pasos para deploy:

1. **Commit y push:**
   ```bash
   git add api/serializers.py api/views.py
   git commit -m "feat: Optimizar endpoint solicitudes con select_related y agregar nombre_usuario"
   git push origin main
   ```

2. **Deploy automático en Render:** El servicio se reiniciará automáticamente.

3. **Verificar con el frontend:** Actualizar las columnas de la tabla para usar `nombre_usuario` y `fecha_solicitud`.

---

## Mapeo Sugerido para el Frontend

### Tabla de Solicitudes:

```jsx
// Antes (mostraba N/A)
<td>{solicitud.usuario || 'N/A'}</td>
<td>{solicitud.fecha || 'N/A'}</td>

// Después (con los nuevos campos)
<td>{solicitud.nombre_usuario || 'Sin usuario'}</td>
<td>{solicitud.fecha_solicitud || 'Sin fecha'}</td>
```

### O usar objetos expandidos:

```jsx
<td>{solicitud.usuario?.nombre_completo || 'Sin usuario'}</td>
<td>{solicitud.fecha_solicitud || solicitud.fecha_creacion?.split('T')[0] || 'Sin fecha'}</td>
```

---

## Resumen de Beneficios

✅ **Usuario siempre disponible:** `nombre_usuario` es un campo directo con el nombre completo  
✅ **Fecha siempre disponible:** `fecha_solicitud` es un alias de `fecha_creacion` en formato ISO  
✅ **Mejor performance:** `select_related` reduce queries de N+1 a 1  
✅ **Sin breaking changes:** POST y PATCH funcionan igual que antes  
✅ **Sin migraciones:** Cambios solo en código Python, no en BD  

---

## Contacto

Para dudas o problemas, verificar que el frontend esté usando los campos correctos según este documento.
