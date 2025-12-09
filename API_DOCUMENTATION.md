# MantenTask API - Documentación de Endpoints

## URL Base
```
http://127.0.0.1:8000/api/
```

## Endpoints Disponibles

### 1. Tipos de Usuario
- **GET** `/api/tipos-usuario/` - Listar todos los tipos de usuario
- **POST** `/api/tipos-usuario/` - Crear nuevo tipo de usuario
- **GET** `/api/tipos-usuario/{id}/` - Obtener tipo de usuario específico
- **PUT/PATCH** `/api/tipos-usuario/{id}/` - Actualizar tipo de usuario
- **DELETE** `/api/tipos-usuario/{id}/` - Eliminar tipo de usuario

### 2. Niveles de Acceso
- **GET** `/api/niveles-acceso/` - Listar todos los niveles de acceso
- **POST** `/api/niveles-acceso/` - Crear nuevo nivel de acceso
- **GET** `/api/niveles-acceso/{id}/` - Obtener nivel de acceso específico
- **PUT/PATCH** `/api/niveles-acceso/{id}/` - Actualizar nivel de acceso
- **DELETE** `/api/niveles-acceso/{id}/` - Eliminar nivel de acceso

### 3. Sucursales
- **GET** `/api/sucursales/` - Listar todas las sucursales
- **POST** `/api/sucursales/` - Crear nueva sucursal
- **GET** `/api/sucursales/{id}/` - Obtener sucursal específica
- **PUT/PATCH** `/api/sucursales/{id}/` - Actualizar sucursal
- **DELETE** `/api/sucursales/{id}/` - Eliminar sucursal

**Filtros:**
- `?search={nombre}` - Buscar por nombre

### 4. Usuarios
- **GET** `/api/usuarios/` - Listar todos los usuarios
- **POST** `/api/usuarios/` - Crear nuevo usuario
- **GET** `/api/usuarios/{id}/` - Obtener usuario específico
- **PUT/PATCH** `/api/usuarios/{id}/` - Actualizar usuario
- **DELETE** `/api/usuarios/{id}/` - Eliminar usuario
- **GET** `/api/usuarios/me/` - Obtener información del usuario actual
- **GET** `/api/usuarios/ingenieros/` - Listar solo ingenieros
- **GET** `/api/usuarios/encargados/` - Listar solo encargados

**Filtros:**
- `?codigo_tipo_usuario={1|2}` - Filtrar por tipo
- `?codigo_nivel_acceso={1-4}` - Filtrar por nivel de acceso
- `?codigo_sucursal={id}` - Filtrar por sucursal
- `?is_active={true|false}` - Filtrar por estado activo
- `?search={texto}` - Buscar en nombre, apellidos, email

**Ejemplo POST crear usuario:**
```json
{
  "username": "jperez",
  "first_name": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "correo_electronico": "juan.perez@empresa.com",
  "password": "Password123!",
  "codigo_tipo_usuario": 1,
  "codigo_nivel_acceso": 3,
  "codigo_sucursal": 1
}
```

### 5. Estados
- **GET** `/api/estados/` - Listar todos los estados
- **POST** `/api/estados/` - Crear nuevo estado
- **GET** `/api/estados/{id}/` - Obtener estado específico
- **PUT/PATCH** `/api/estados/{id}/` - Actualizar estado
- **DELETE** `/api/estados/{id}/` - Eliminar estado

### 6. Máquinas
- **GET** `/api/maquinas/` - Listar todas las máquinas
- **POST** `/api/maquinas/` - Crear nueva máquina
- **GET** `/api/maquinas/{id}/` - Obtener máquina específica
- **PUT/PATCH** `/api/maquinas/{id}/` - Actualizar máquina
- **DELETE** `/api/maquinas/{id}/` - Eliminar máquina
- **GET** `/api/maquinas/por_sucursal/?sucursal={id}` - Listar por sucursal
- **POST** `/api/maquinas/{id}/registrar_mantenimiento/` - Registrar fecha mantenimiento

**Filtros:**
- `?codigo_sucursal={id}` - Filtrar por sucursal
- `?marca={marca}` - Filtrar por marca
- `?search={texto}` - Buscar en modelo y marca

**Ejemplo POST crear máquina:**
```json
{
  "codigo_sucursal": 1,
  "modelo": "Industrial XL-2000",
  "marca": "Siemens",
  "fecha_compra": "2024-01-15",
  "fecha_instalacion": "2024-02-01"
}
```

### 7. Solicitudes (Tickets)
- **GET** `/api/solicitudes/` - Listar todas las solicitudes
- **POST** `/api/solicitudes/` - Crear nueva solicitud
- **GET** `/api/solicitudes/{id}/` - Obtener solicitud específica
- **PUT/PATCH** `/api/solicitudes/{id}/` - Actualizar solicitud
- **DELETE** `/api/solicitudes/{id}/` - Eliminar solicitud
- **GET** `/api/solicitudes/pendientes/` - Listar solicitudes pendientes
- **GET** `/api/solicitudes/completadas/` - Listar solicitudes completadas
- **POST** `/api/solicitudes/{id}/cambiar_estado/` - Cambiar estado de solicitud

**Filtros:**
- `?codigo_estado={id}` - Filtrar por estado
- `?codigo_maquinaria={id}` - Filtrar por máquina
- `?id_usuario={id}` - Filtrar por usuario
- `?search={texto}` - Buscar en descripción

**Ejemplo POST crear solicitud:**
```json
{
  "codigo_maquinaria": 1,
  "id_usuario": 1,
  "descripcion": "La máquina presenta ruidos extraños y vibración excesiva",
  "codigo_estado": 1
}
```

**Ejemplo POST cambiar estado:**
```json
{
  "codigo_estado": 2
}
```

### 8. Informes
- **GET** `/api/informes/` - Listar todos los informes
- **POST** `/api/informes/` - Crear nuevo informe (genera PDF automático)
- **GET** `/api/informes/{id}/` - Obtener informe específico
- **PUT/PATCH** `/api/informes/{id}/` - Actualizar informe
- **DELETE** `/api/informes/{id}/` - Eliminar informe
- **GET** `/api/informes/{id}/descargar_pdf/` - Descargar PDF del informe
- **POST** `/api/informes/{id}/regenerar_pdf/` - Regenerar PDF
- **POST** `/api/informes/{id}/enviar_por_correo/` - Enviar por email

**Filtros:**
- `?codigo_maquinaria={id}` - Filtrar por máquina
- `?id_usuario={id}` - Filtrar por usuario

**Ejemplo POST crear informe:**
```json
{
  "codigo_solicitud": 1,
  "codigo_maquinaria": 1,
  "id_usuario": 1,
  "descripcion": "Se realizó limpieza profunda, reemplazo de rodamientos y calibración. La máquina ahora opera correctamente sin vibraciones."
}
```

**Ejemplo POST enviar por correo:**
```json
{
  "email": "destinatario@empresa.com"
}
```

## Funcionalidades Automáticas

### Notificaciones por Correo
El sistema envía notificaciones automáticas en los siguientes casos:
1. **Nueva solicitud creada** - Se notifica a todos los ingenieros activos
2. **Cambio de estado** - Se notifica al usuario que creó la solicitud

Para activar las notificaciones reales, configura en `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app
DEFAULT_FROM_EMAIL=mantentask@empresa.com
```

### Generación Automática de PDF
Los informes generan automáticamente un PDF al ser creados. El PDF incluye:
- Información general del informe
- Datos de la máquina
- Descripción del problema y trabajo realizado
- Fecha y usuario que lo generó

## Paginación
Todos los listados están paginados con 10 elementos por página:
- `?page=2` - Segunda página
- `?page_size=20` - Cambiar tamaño de página

## Ordenamiento
Usa `?ordering=` con los campos disponibles:
- `/api/solicitudes/?ordering=-fecha_creacion` - Más recientes primero
- `/api/maquinas/?ordering=marca,modelo` - Por marca y modelo

## Estados del Sistema
1. **Pendiente** - Solicitud recién creada
2. **En Proceso** - Solicitud siendo atendida
3. **Completado** - Solicitud finalizada
4. **Cancelado** - Solicitud cancelada

## Tipos de Usuario
1. **Ingeniero** - Personal técnico que atiende solicitudes
2. **Encargado** - Supervisor que crea y consulta solicitudes

## Niveles de Acceso
1. **Básico** - Acceso limitado
2. **Intermedio** - Acceso moderado
3. **Avanzado** - Acceso amplio
4. **Administrador** - Acceso total

## Panel de Administración
Accede a `http://127.0.0.1:8000/admin/` con un superusuario para gestionar todos los datos del sistema.
