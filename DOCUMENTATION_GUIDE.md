# Documentación Generada - MantenTask API

## Archivos de Documentación Creados

Este proyecto ahora tiene documentación completa para frontend y backend.

### 📋 Archivos de Documentación

1. **API_COMPLETE_DOCS.md** - Documentación completa de la API
   - Todos los endpoints
   - Métodos de autenticación
   - Ejemplos de requests/responses
   - Códigos de error
   - Flujos completos de ejemplo

2. **FRONTEND_REACT_SETUP.md** - Guía de integración React + Axios
   - Instalación de dependencias
   - Configuración de Axios
   - Ejemplos de uso de todos los endpoints
   - Context API para autenticación
   - Manejo de errores
   - Estructura de carpetas recomendada

3. **EXAMPLE_REACT_PROJECT.md** - Proyecto React de ejemplo
   - Código listo para usar
   - Estructura de carpetas completa
   - Componentes de ejemplo
   - Pasos para crear el proyecto
   - Credenciales de prueba

4. **API_DOCUMENTATION.md** - Documentación original (se mantiene)

5. **EMAIL_CONFIG.md** - Configuración de correos (se mantiene)

6. **README.md** - Documentación original (se mantiene)

---

## Resumen Rápido

### Backend (Django)
- ✅ **URL Base:** `http://127.0.0.1:8000/api/`
- ✅ **Autenticación:** Session Authentication (Cookies)
- ✅ **Endpoints:** 8+ resources con CRUD completo
- ✅ **Notificaciones:** Correos automáticos
- ✅ **PDFs:** Generación automática de informes

### Frontend (React + Axios)
```bash
npm install axios react-router-dom
npm run dev
```

**Usuarios de prueba:**
- Usuario: `jperez` / Contraseña: `ingeniero123`
- Usuario: `admin` / Contraseña: `admin123`

---

## Endpoints Principales

### Autenticación
```
POST   /api/auth/login/          - Iniciar sesión
POST   /api/auth/logout/         - Cerrar sesión
GET    /api/auth/me/             - Usuario actual
POST   /api/auth/register/       - Registrar usuario
```

### Recursos (CRUD completo)
```
/api/usuarios/                   - Usuarios
/api/maquinas/                   - Máquinas
/api/solicitudes/                - Solicitudes (Tickets)
/api/informes/                   - Informes
/api/sucursales/                 - Sucursales
```

### Catálogos (Solo lectura)
```
/api/tipos-usuario/              - Tipos de usuario
/api/niveles-acceso/             - Niveles de acceso
/api/estados/                    - Estados de solicitudes
```

---

## Estructura del Backend

```
api/
├── auth.py              ← Endpoints de autenticación (nuevo)
├── views.py             ← ViewSets del API
├── serializers.py       ← Serializadores
├── models.py            ← Modelos de BD
├── urls.py              ← Rutas (actualizado)
└── management/
    └── commands/
        ├── init_data.py ← Crea catálogos
        └── create_test_data.py ← Crea datos de prueba

mantentask_project/
├── settings.py          ← Configuración (actualizado con auth)
├── middleware.py        ← Middleware CSRF (nuevo)
└── urls.py
```

---

## Quick Start para Frontend

### 1. Crear proyecto React
```bash
npm create vite@latest mantentask-frontend -- --template react
cd mantentask-frontend
npm install axios react-router-dom
```

### 2. Crear estructura
```
src/
├── api/
│   ├── axiosConfig.js      ← Ver FRONTEND_REACT_SETUP.md
│   ├── auth.js
│   ├── solicitudes.js
│   └── ...
├── context/
│   └── AuthContext.js      ← Ver FRONTEND_REACT_SETUP.md
├── components/
│   ├── LoginForm.jsx       ← Ver EXAMPLE_REACT_PROJECT.md
│   └── Dashboard.jsx
└── App.jsx
```

### 3. Iniciar servidor
```bash
npm run dev
# Acceder a http://localhost:3000
```

### 4. Probar login
- Usuario: `jperez`
- Contraseña: `ingeniero123`

---

## Características Implementadas

### Backend
- ✅ Session Authentication (Cookies)
- ✅ CRUD completo de recursos
- ✅ Notificaciones por email automáticas
- ✅ Generación de PDFs
- ✅ Filtros y búsquedas
- ✅ Paginación
- ✅ Protección CSRF deshabilitada para API (desarrollo)
- ✅ CORS habilitado

### Frontend (Documentado)
- ✅ Configuración de Axios con withCredentials
- ✅ Context API para autenticación
- ✅ Protección de rutas
- ✅ Ejemplos de CRUD completo
- ✅ Manejo de errores
- ✅ Descarga de PDFs
- ✅ Formularios de ejemplo

---

## Próximos Pasos

### Para el Backend
1. Implementar refresh tokens (para mayor seguridad)
2. Agregar roles/permisos más granulares
3. Agregar logs auditoria
4. Documentación Swagger/OpenAPI (opcional)

### Para el Frontend
1. Crear todos los componentes
2. Agregar validación de formularios
3. Agregar notificaciones UI
4. Mejorar diseño visual
5. Agregar paginación en listados
6. Implementar filtros avanzados
7. Agregar gráficos de estadísticas

---

## Documentos a Consultar

| Documento | Contenido |
|-----------|----------|
| API_COMPLETE_DOCS.md | Referencia completa de endpoints |
| FRONTEND_REACT_SETUP.md | Guía de integración con React |
| EXAMPLE_REACT_PROJECT.md | Código listo para usar |
| EMAIL_CONFIG.md | Configuración de correos |

---

## Soporte

Si necesitas ayuda:

1. Consulta la documentación en el archivo correspondiente
2. Revisa los ejemplos en EXAMPLE_REACT_PROJECT.md
3. Prueba los endpoints en Postman primero
4. Verifica los logs del servidor Django

---

**Última actualización:** Diciembre 10, 2025

**Sistema:** MantenTask Backend API + Frontend React
