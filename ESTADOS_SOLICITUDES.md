# Sistema de Gestión de Estados de Solicitudes

## Códigos de Estado

El sistema maneja tres estados principales para las solicitudes de mantenimiento:

| Código | Nombre | Descripción | Color sugerido |
|--------|--------|-------------|----------------|
| **1** | **Pendiente** | Solicitud creada, esperando asignación de ingeniero | 🟡 Amarillo |
| **2** | **En Proceso** | Ingeniero trabajando en la solicitud | 🔵 Azul |
| **3** | **Completada** | Trabajo finalizado | 🟢 Verde |

---

## Flujo de Estados

```
┌─────────────┐
│  Pendiente  │ (1)
│  (Creada)   │
└──────┬──────┘
       │
       │ Encargado asigna ingeniero
       │ POST /api/solicitudes/{id}/asignar_ingeniero/
       │
       ▼
┌─────────────┐
│  Pendiente  │ (1)
│  (Asignada) │
└──────┬──────┘
       │
       │ Ingeniero acepta y comienza trabajo
       │ POST /api/solicitudes/{id}/cambiar_estado/ {"codigo_estado": 2}
       │
       ▼
┌─────────────┐
│ En Proceso  │ (2)
└──────┬──────┘
       │
       │ Ingeniero completa trabajo y crea informe
       │ POST /api/solicitudes/{id}/cambiar_estado/ {"codigo_estado": 3}
       │
       ▼
┌─────────────┐
│ Completada  │ (3)
└─────────────┘
```

---

## Endpoints de Gestión de Estados

### 1. Cambiar Estado de Solicitud

**Endpoint:** `POST /api/solicitudes/{id}/cambiar_estado/`

**Request Body:**
```json
{
  "codigo_estado": 2
}
```

**Response (200 OK):**
```json
{
  "codigo_solicitud": 5,
  "codigo_estado": 2,
  "estado": {
    "codigo_estado": 2,
    "nombre_estado": "En Proceso"
  },
  "mensaje": "Estado actualizado correctamente a En Proceso",
  ...otros campos...
}
```

**Reglas de Negocio:**

| Tipo de Usuario | Permisos |
|----------------|----------|
| **Administrador** (nivel_acceso=4) | ✅ Puede cambiar cualquier solicitud a cualquier estado |
| **Encargado** (tipo_usuario=2) | ✅ Puede cambiar cualquier solicitud a cualquier estado |
| **Ingeniero** (tipo_usuario=1) | ⚠️ Solo puede cambiar solicitudes asignadas a él<br>⚠️ Solo puede avanzar estados (1→2→3), no retroceder |
| **Usuario normal** | ❌ No puede cambiar estados |

**Validaciones:**
- ✅ `codigo_estado` debe ser 1, 2 o 3
- ✅ Usuario debe tener permisos según su rol
- ✅ Ingenieros no pueden retroceder estados
- ✅ Ingenieros solo pueden cambiar sus solicitudes asignadas

**Códigos de Respuesta:**
- `200 OK`: Estado cambiado exitosamente
- `400 Bad Request`: Estado inválido o intento de retroceder estado
- `403 Forbidden`: Usuario no autorizado
- `404 Not Found`: Solicitud no existe

---

### 2. Asignar Ingeniero a Solicitud

**Endpoint:** `POST /api/solicitudes/{id}/asignar_ingeniero/`

**Request Body:**
```json
{
  "id_ingeniero": 10
}
```

**Response (200 OK):**
```json
{
  "codigo_solicitud": 5,
  "ingeniero_asignado": 10,
  "ingeniero": {
    "id_usuario": 10,
    "username": "jperez",
    "nombre_completo": "Juan Pérez García",
    "correo_electronico": "jperez@example.com"
  },
  "nombre_ingeniero": "Juan Pérez García",
  "mensaje": "Ingeniero Juan Pérez García asignado correctamente",
  ...otros campos...
}
```

**Reglas de Negocio:**
- Solo **encargados** y **administradores** pueden asignar ingenieros
- El `id_ingeniero` debe corresponder a un usuario activo con `codigo_tipo_usuario=1` (Ingeniero)

**Validaciones:**
- ✅ Usuario debe ser encargado o administrador
- ✅ `id_ingeniero` debe existir y ser ingeniero activo
- ✅ Se actualiza el campo `ingeniero_asignado` de la solicitud

**Códigos de Respuesta:**
- `200 OK`: Ingeniero asignado exitosamente
- `400 Bad Request`: `id_ingeniero` faltante
- `403 Forbidden`: Usuario no autorizado (no es encargado/admin)
- `404 Not Found`: Ingeniero no encontrado o no válido

---

## Filtros de Listado

### GET /api/solicitudes/

El endpoint de listado soporta los siguientes filtros:

#### Filtros por Estado (Query Params)

| Query Param | Descripción | Ejemplo |
|------------|-------------|---------|
| `codigo_estado=1` | Filtra por código de estado exacto | `/api/solicitudes/?codigo_estado=1` |
| `pendientes=true` | Alias para `codigo_estado=1` | `/api/solicitudes/?pendientes=true` |
| `en_proceso=true` | Alias para `codigo_estado=2` | `/api/solicitudes/?en_proceso=true` |
| `completadas=true` | Alias para `codigo_estado=3` | `/api/solicitudes/?completadas=true` |

#### Filtros por Ingeniero

| Query Param | Descripción | Ejemplo |
|------------|-------------|---------|
| `id_ingeniero=10` | Solicitudes asignadas a un ingeniero específico | `/api/solicitudes/?id_ingeniero=10` |
| `ingeniero_asignado__isnull=true` | Solicitudes sin ingeniero asignado | (usar filtro Django) |

#### Otros Filtros (ya existentes)

| Query Param | Descripción |
|------------|-------------|
| `codigo_maquinaria=5` | Solicitudes de una máquina específica |
| `id_usuario=3` | Solicitudes creadas por un usuario |
| `codigo_maquinaria__codigo_sucursal=2` | Solicitudes de una sucursal |

---

## Ejemplos de Uso

### Ejemplo 1: Encargado crea y asigna solicitud

```bash
# 1. Crear solicitud
POST /api/solicitudes/
Authorization: Bearer <token_encargado>
Content-Type: application/json

{
  "codigo_maquinaria": 5,
  "descripcion": "Máquina hace ruido extraño",
  "fecha_programada": "2025-12-20"
}

# Response: solicitud creada con codigo_estado=1 (Pendiente)

# 2. Asignar ingeniero
POST /api/solicitudes/15/asignar_ingeniero/
Authorization: Bearer <token_encargado>
Content-Type: application/json

{
  "id_ingeniero": 10
}

# Response: ingeniero asignado exitosamente
```

### Ejemplo 2: Ingeniero procesa solicitud

```bash
# 1. Ver solicitudes asignadas a mí
GET /api/solicitudes/?id_ingeniero=10
Authorization: Bearer <token_ingeniero>

# 2. Marcar como "En Proceso"
POST /api/solicitudes/15/cambiar_estado/
Authorization: Bearer <token_ingeniero>
Content-Type: application/json

{
  "codigo_estado": 2
}

# 3. Al finalizar, marcar como "Completada"
POST /api/solicitudes/15/cambiar_estado/
Authorization: Bearer <token_ingeniero>
Content-Type: application/json

{
  "codigo_estado": 3
}
```

### Ejemplo 3: Dashboard de estados

```bash
# Contar solicitudes por estado
GET /api/solicitudes/?pendientes=true
# Total: X solicitudes pendientes

GET /api/solicitudes/?en_proceso=true
# Total: Y solicitudes en proceso

GET /api/solicitudes/?completadas=true
# Total: Z solicitudes completadas
```

---

## Respuesta de Listado (GET /api/solicitudes/)

**Formato de cada solicitud:**

```json
{
  "codigo_solicitud": 15,
  "codigo_maquinaria": 5,
  "maquina": {
    "codigo_maquinaria": 5,
    "modelo": "Modelo X",
    "marca": "Marca Y",
    "numero_serie": "SN-12345"
  },
  "id_usuario": 3,
  "usuario": {
    "id_usuario": 3,
    "username": "mcampos",
    "nombre_completo": "María Campos López",
    "correo_electronico": "mcampos@example.com"
  },
  "nombre_usuario": "María Campos López",
  "ingeniero_asignado": 10,
  "ingeniero": {
    "id_usuario": 10,
    "username": "jperez",
    "nombre_completo": "Juan Pérez García",
    "correo_electronico": "jperez@example.com"
  },
  "nombre_ingeniero": "Juan Pérez García",
  "descripcion": "Máquina hace ruido extraño",
  "codigo_estado": 2,
  "estado": {
    "codigo_estado": 2,
    "nombre_estado": "En Proceso"
  },
  "fecha_creacion": "2025-12-16T10:30:00Z",
  "fecha_solicitud": "2025-12-16",
  "fecha_programada": "2025-12-20",
  "fecha_actualizacion": "2025-12-16T14:25:00Z",
  "tiene_informe": false
}
```

**Campos de Estado:**
- `codigo_estado`: ID numérico (1, 2 o 3)
- `estado`: Objeto expandido con `codigo_estado` y `nombre_estado`
- `estado.nombre_estado`: Texto legible ("Pendiente", "En Proceso", "Completada")

**Campos de Ingeniero:**
- `ingeniero_asignado`: ID del ingeniero (puede ser `null`)
- `ingeniero`: Objeto expandido con datos del ingeniero (puede ser `null`)
- `nombre_ingeniero`: Nombre completo del ingeniero (puede ser `null`)

---

## Mapeo para Frontend

### Mostrar Estado con Color

```jsx
const getEstadoColor = (codigoEstado) => {
  switch(codigoEstado) {
    case 1: return 'warning';  // Amarillo
    case 2: return 'info';     // Azul
    case 3: return 'success';  // Verde
    default: return 'default';
  }
};

// Uso
<Badge color={getEstadoColor(solicitud.codigo_estado)}>
  {solicitud.estado?.nombre_estado || 'Desconocido'}
</Badge>
```

### Dashboard de Contadores

```jsx
const [estadisticas, setEstadisticas] = useState({
  pendientes: 0,
  en_proceso: 0,
  completadas: 0
});

// Cargar datos
const cargarEstadisticas = async () => {
  const [pendientes, enProceso, completadas] = await Promise.all([
    api.get('/solicitudes/?pendientes=true'),
    api.get('/solicitudes/?en_proceso=true'),
    api.get('/solicitudes/?completadas=true')
  ]);
  
  setEstadisticas({
    pendientes: pendientes.data.length,
    en_proceso: enProceso.data.length,
    completadas: completadas.data.length
  });
};
```

### Cambiar Estado desde Frontend

```jsx
const cambiarEstado = async (solicitudId, nuevoEstado) => {
  try {
    const response = await api.post(
      `/solicitudes/${solicitudId}/cambiar_estado/`,
      { codigo_estado: nuevoEstado }
    );
    
    toast.success(response.data.mensaje);
    // Recargar solicitudes
    recargarSolicitudes();
  } catch (error) {
    if (error.response?.status === 403) {
      toast.error('No tienes permiso para cambiar el estado');
    } else if (error.response?.status === 400) {
      toast.error(error.response.data.error);
    } else {
      toast.error('Error al cambiar estado');
    }
  }
};
```

---

## Migraciones

### Migración 0005 - Campo ingeniero_asignado

La migración `0005_solicitud_ingeniero_asignado_and_more.py` agrega:
- Campo `ingeniero_asignado` (ForeignKey a Usuario, nullable)
- Actualiza `related_name` de `id_usuario` a `solicitudes_creadas`

**Aplicar migración en producción:**
```bash
python manage.py migrate api
```

---

## Logging

Los cambios de estado y asignaciones se registran en los logs del sistema:

```
Usuario mcampos cambió estado de solicitud #15 de Pendiente a En Proceso
Usuario admin asignó ingeniero jperez a solicitud #15
```

---

## Notas Importantes

1. **Estados no retroactivos para ingenieros:** Los ingenieros no pueden cambiar una solicitud de "Completada" a "En Proceso". Solo admins y encargados pueden hacerlo.

2. **Ingeniero asignado opcional:** Una solicitud puede existir sin ingeniero asignado. En ese caso, ningún ingeniero puede cambiar su estado.

3. **Formato de respuesta consistente:** El frontend siempre recibe tanto `codigo_estado` (número) como `estado` (objeto expandido) para flexibilidad.

4. **Filtros acumulables:** Se pueden combinar filtros: `/api/solicitudes/?pendientes=true&id_ingeniero=10`

---

## Troubleshooting

### Problema: Frontend muestra "Desconocido"

**Solución:** Verificar que se use `solicitud.estado?.nombre_estado` en lugar de solo `solicitud.estado`

### Problema: Ingeniero no puede cambiar estado

**Causas posibles:**
- Solicitud no asignada a él → Verificar `solicitud.ingeniero_asignado`
- Intenta retroceder estado (ej: 3→2) → Solo puede avanzar
- Usuario no es ingeniero → Verificar `codigo_tipo_usuario=1`

### Problema: No se puede asignar ingeniero

**Causas posibles:**
- Usuario no es encargado/admin → Verificar permisos
- ID de ingeniero inválido → Verificar que exista y sea tipo=1
- Ingeniero inactivo → Verificar `is_active=True`

---

## Resumen de Cambios Implementados

✅ Campo `ingeniero_asignado` en modelo `Solicitud`  
✅ Endpoint `POST /api/solicitudes/{id}/cambiar_estado/` con validaciones de permisos  
✅ Endpoint `POST /api/solicitudes/{id}/asignar_ingeniero/`  
✅ Filtros por estado: `pendientes`, `en_proceso`, `completadas`  
✅ Filtro por ingeniero: `id_ingeniero`  
✅ Optimización de queries con `select_related`  
✅ Documentación completa de códigos de estado  
✅ Migración 0005 para nuevo campo  

---

## Contacto y Soporte

Para dudas sobre la implementación, referirse a este documento y al código en:
- Modelo: `api/models.py` → Clase `Solicitud`
- Serializers: `api/serializers.py` → `SolicitudSerializer`
- Views: `api/views.py` → `SolicitudViewSet`
