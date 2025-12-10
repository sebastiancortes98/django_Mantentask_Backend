# MantenTask API - Documentación Completa

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [Endpoints](#endpoints)
4. [Errores](#errores)
5. [Ejemplos](#ejemplos)

---

## Introducción

**URL Base:** `http://127.0.0.1:8000/api/`

**Método de Autenticación:** Session Authentication (Cookies)

**Formato de Respuesta:** JSON

---

## Autenticación

### Login
Inicia sesión con usuario y contraseña.

**Endpoint:** `POST /api/auth/login/`

**Body:**
```json
{
  "username": "jperez",
  "password": "ingeniero123"
}
```

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Login exitoso",
  "user": {
    "id_usuario": 2,
    "username": "jperez",
    "first_name": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "correo_electronico": "juan.perez@empresa.com",
    "codigo_tipo_usuario": 1,
    "codigo_nivel_acceso": 3,
    "codigo_sucursal": 1,
    "nombre_completo": "Juan Pérez García",
    "is_active": true,
    "date_joined": "2025-12-10T15:30:00Z"
  }
}
```

**Notas:**
- Las cookies de sesión se envían automáticamente
- El navegador/cliente debe almacenarlas para requests posteriores

---

### Registrar Usuario
Registra un nuevo usuario en el sistema.

**Endpoint:** `POST /api/auth/register/`

**Body:**
```json
{
  "username": "nuevo_usuario",
  "password": "SecurePass123!",
  "first_name": "Carlos",
  "apellido_paterno": "López",
  "apellido_materno": "García",
  "correo_electronico": "carlos@empresa.com",
  "codigo_tipo_usuario": 1,
  "codigo_nivel_acceso": 2,
  "codigo_sucursal": 1
}
```

**Respuesta (201):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user": {
    "id_usuario": 10,
    "username": "nuevo_usuario",
    ...
  }
}
```

**Códigos de Tipo Usuario:**
- `1` = Ingeniero
- `2` = Encargado

**Códigos de Nivel de Acceso:**
- `1` = Básico
- `2` = Intermedio
- `3` = Avanzado
- `4` = Administrador

---

### Obtener Usuario Actual
Obtiene información del usuario logueado.

**Endpoint:** `GET /api/auth/me/`

**Requiere:** Autenticación ✅

**Respuesta (200):**
```json
{
  "success": true,
  "user": {
    "id_usuario": 2,
    "username": "jperez",
    ...
  }
}
```

---

### Logout
Cierra la sesión actual.

**Endpoint:** `POST /api/auth/logout/`

**Requiere:** Autenticación ✅

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Logout exitoso"
}
```

---

## Endpoints

### Usuarios

#### Listar usuarios
**GET** `/api/usuarios/`

**Parámetros opcionales:**
- `?search=texto` - Buscar por nombre, apellido, email
- `?codigo_tipo_usuario=1` - Filtrar por tipo (1=Ingeniero, 2=Encargado)
- `?codigo_nivel_acceso=3` - Filtrar por nivel
- `?codigo_sucursal=1` - Filtrar por sucursal
- `?is_active=true` - Filtrar por estado activo
- `?page=2` - Número de página
- `?page_size=20` - Registros por página

**Requiere:** No ❌

---

#### Crear usuario
**POST** `/api/usuarios/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "username": "nuevo_user",
  "first_name": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "correo_electronico": "juan@empresa.com",
  "password": "Pass123!",
  "codigo_tipo_usuario": 1,
  "codigo_nivel_acceso": 3,
  "codigo_sucursal": 1
}
```

---

#### Obtener usuario específico
**GET** `/api/usuarios/{id}/`

**Requiere:** No ❌

---

#### Actualizar usuario
**PATCH** `/api/usuarios/{id}/`

**Requiere:** Autenticación ✅

**Body (opcional):**
```json
{
  "first_name": "Juan",
  "correo_electronico": "nuevo@empresa.com",
  "codigo_nivel_acceso": 4
}
```

---

#### Eliminar usuario
**DELETE** `/api/usuarios/{id}/`

**Requiere:** Autenticación ✅

---

#### Usuarios especiales
**GET** `/api/usuarios/ingenieros/` - Listar solo ingenieros

**GET** `/api/usuarios/encargados/` - Listar solo encargados

---

### Sucursales

#### Listar
**GET** `/api/sucursales/`

**Parámetros:** `?search=nombre` `?page=X`

---

#### Crear
**POST** `/api/sucursales/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "nombre_sucursal": "Sucursal Centro"
}
```

---

#### Actualizar
**PATCH** `/api/sucursales/{id}/`

**Requiere:** Autenticación ✅

---

#### Eliminar
**DELETE** `/api/sucursales/{id}/`

**Requiere:** Autenticación ✅

---

### Máquinas

#### Listar
**GET** `/api/maquinas/`

**Parámetros:**
- `?codigo_sucursal=1` - Filtrar por sucursal
- `?marca=Siemens` - Filtrar por marca
- `?search=modelo` - Buscar

---

#### Crear
**POST** `/api/maquinas/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "codigo_sucursal": 1,
  "modelo": "Industrial XL-2000",
  "marca": "Siemens",
  "fecha_compra": "2024-01-15",
  "fecha_instalacion": "2024-02-01"
}
```

---

#### Obtener
**GET** `/api/maquinas/{id}/`

---

#### Actualizar
**PATCH** `/api/maquinas/{id}/`

**Requiere:** Autenticación ✅

---

#### Eliminar
**DELETE** `/api/maquinas/{id}/`

**Requiere:** Autenticación ✅

---

#### Registrar mantenimiento
**POST** `/api/maquinas/{id}/registrar_mantenimiento/`

**Requiere:** Autenticación ✅

**Actualiza** `fecha_ultima_mantencion` a la fecha actual

---

### Solicitudes

#### Listar
**GET** `/api/solicitudes/`

**Parámetros:**
- `?codigo_estado=1` - Filtrar por estado
- `?codigo_maquinaria=1` - Filtrar por máquina
- `?id_usuario=2` - Filtrar por usuario
- `?search=texto` - Buscar en descripción
- `?ordering=-fecha_creacion` - Más recientes primero

---

#### Crear
**POST** `/api/solicitudes/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "codigo_maquinaria": 1,
  "id_usuario": 2,
  "descripcion": "La máquina presenta ruidos extraños",
  "codigo_estado": 1
}
```

**⚠️ Nota:** Al crear, automáticamente se envía email a todos los ingenieros activos

---

#### Obtener
**GET** `/api/solicitudes/{id}/`

---

#### Actualizar
**PATCH** `/api/solicitudes/{id}/`

**Requiere:** Autenticación ✅

---

#### Eliminar
**DELETE** `/api/solicitudes/{id}/`

**Requiere:** Autenticación ✅

---

#### Cambiar estado
**POST** `/api/solicitudes/{id}/cambiar_estado/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "codigo_estado": 2
}
```

**Estados disponibles:**
- `1` = Pendiente
- `2` = En Proceso
- `3` = Completado
- `4` = Cancelado

**⚠️ Nota:** Al cambiar estado, se envía email al usuario que creó la solicitud

---

#### Solicitudes especiales
**GET** `/api/solicitudes/pendientes/` - Listar pendientes/en proceso

**GET** `/api/solicitudes/completadas/` - Listar completadas

---

### Informes

#### Listar
**GET** `/api/informes/`

**Parámetros:**
- `?codigo_maquinaria=1` - Filtrar por máquina
- `?id_usuario=2` - Filtrar por usuario

---

#### Crear
**POST** `/api/informes/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "codigo_solicitud": 1,
  "codigo_maquinaria": 1,
  "id_usuario": 2,
  "descripcion": "Se realizó limpieza profunda, reemplazo de rodamientos y calibración."
}
```

**⚠️ Nota:** Se genera automáticamente un PDF

---

#### Obtener
**GET** `/api/informes/{id}/`

---

#### Actualizar
**PATCH** `/api/informes/{id}/`

**Requiere:** Autenticación ✅

---

#### Eliminar
**DELETE** `/api/informes/{id}/`

**Requiere:** Autenticación ✅

---

#### Descargar PDF
**GET** `/api/informes/{id}/descargar_pdf/`

**Respuesta:** Archivo PDF descargable

---

#### Regenerar PDF
**POST** `/api/informes/{id}/regenerar_pdf/`

**Requiere:** Autenticación ✅

---

#### Enviar por correo
**POST** `/api/informes/{id}/enviar_por_correo/`

**Requiere:** Autenticación ✅

**Body:**
```json
{
  "email": "destinatario@empresa.com"
}
```

**⚠️ Nota:** Envía el PDF como adjunto por correo electrónico

---

### Catálogos (Solo lectura)

**GET** `/api/tipos-usuario/` - Tipos de usuario

**GET** `/api/niveles-acceso/` - Niveles de acceso

**GET** `/api/estados/` - Estados de solicitudes

---

## Errores

### 400 Bad Request
```json
{
  "error": "Descripción del error"
}
```

### 401 Unauthorized
```json
{
  "detail": "Credenciales inválidas o sesión expirada"
}
```

### 403 Forbidden
```json
{
  "detail": "No tienes permiso para realizar esta acción"
}
```

### 404 Not Found
```json
{
  "detail": "El recurso no fue encontrado"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error interno del servidor"
}
```

---

## Ejemplos

### Flujo completo de creación de solicitud

**1. Login**
```bash
POST /api/auth/login/
Body: {"username": "jperez", "password": "ingeniero123"}
```

**2. Listar máquinas**
```bash
GET /api/maquinas/?codigo_sucursal=1
```

**3. Crear solicitud**
```bash
POST /api/solicitudes/
Body: {
  "codigo_maquinaria": 1,
  "id_usuario": 2,
  "descripcion": "Prueba de vibración",
  "codigo_estado": 1
}
```

**4. Crear informe**
```bash
POST /api/informes/
Body: {
  "codigo_solicitud": 1,
  "codigo_maquinaria": 1,
  "id_usuario": 2,
  "descripcion": "Se realizó mantenimiento"
}
```

**5. Enviar informe por correo**
```bash
POST /api/informes/1/enviar_por_correo/
Body: {"email": "jefe@empresa.com"}
```

**6. Logout**
```bash
POST /api/auth/logout/
```

---

## Notas Importantes

- **Autenticación:** Todas las operaciones de creación/actualización/eliminación requieren estar logueado
- **Paginación:** Los listados están paginados con 10 elementos por página por defecto
- **Correos:** Se envían automáticamente en ciertos eventos (crear solicitud, cambiar estado)
- **PDFs:** Se generan automáticamente al crear informes
- **Cookies:** Se envían automáticamente; el cliente no debe manipularlas
