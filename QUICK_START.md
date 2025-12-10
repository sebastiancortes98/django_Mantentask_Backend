# 📚 Guía de Documentación - Inicio Rápido

## 🎯 ¿Qué necesito leer?

### Si soy **Backend Developer**
1. **API_COMPLETE_DOCS.md** - Referencia de todos los endpoints
2. **EMAIL_CONFIG.md** - Configuración de correos (ya está hecha)

### Si soy **Frontend Developer (React)**
1. **FRONTEND_REACT_SETUP.md** - Guía completa paso a paso
2. **EXAMPLE_REACT_PROJECT.md** - Código de ejemplo listo para copiar
3. **API_COMPLETE_DOCS.md** - Referencia de endpoints

### Si soy **DevOps / Deployment**
1. **README.md** - Instrucciones originales
2. **.env** - Variables de configuración
3. **Dockerfile** - Para Docker
4. **docker-compose.yml** - Para Docker Compose

---

## 🚀 Quick Start (5 minutos)

### Backend (Ya configurado ✅)

```bash
# Inicializar base de datos (primera vez)
python manage.py init_data

# Crear datos de prueba (opcional)
python manage.py create_test_data

# Iniciar servidor
python manage.py runserver
```

**URL:** `http://127.0.0.1:8000/api/`

**Usuarios de prueba:**
- jperez / ingeniero123
- admin / admin123

---

### Frontend (React)

```bash
# 1. Crear proyecto
npm create vite@latest mantentask-frontend -- --template react
cd mantentask-frontend
npm install

# 2. Instalar dependencias
npm install axios react-router-dom

# 3. Copiar archivos de ejemplo
# (Ver EXAMPLE_REACT_PROJECT.md para toda la estructura)

# 4. Iniciar servidor
npm run dev
```

**URL:** `http://localhost:3000`

---

## 📁 Archivos de Documentación

### Backend
```
mantentask-backend/
├── 📄 API_COMPLETE_DOCS.md          ← Lee esto primero
├── 📄 EMAIL_CONFIG.md               ← Configuración de correos
├── 📄 README.md                     ← Info general
├── 📄 DOCUMENTATION_GUIDE.md         ← Esta guía
└── 📄 API_DOCUMENTATION.md          ← Documentación original
```

### Frontend (Documentación)
```
mantentask-backend/
├── 📄 FRONTEND_REACT_SETUP.md       ← Lee esto si usas React
├── 📄 EXAMPLE_REACT_PROJECT.md      ← Código de ejemplo
└── 📄 DOCUMENTATION_GUIDE.md         ← Esta guía
```

---

## 🔐 Flujo de Autenticación

```
1. Usuario ingresa credenciales
   POST /api/auth/login/
   → Recibe cookies de sesión

2. Frontend almacena cookies automáticamente
   (axios con withCredentials: true)

3. Todas las requests posteriores incluyen cookies
   → Servidor reconoce al usuario

4. Al logout
   POST /api/auth/logout/
   → Cookies se limpian
```

### En React:
```javascript
// 1. Login
const { login } = useAuth();
await login(username, password);
// → Cookies automáticamente

// 2. Hacer request autenticada
await apiClient.post('/api/solicitudes/', data);
// → Cookies se envían automáticamente

// 3. Logout
const { logout } = useAuth();
await logout();
// → Cookies se limpian
```

---

## 📊 Arquitectura

```
                    ┌─────────────────────┐
                    │  Frontend (React)   │
                    │  Port: 3000         │
                    └──────────┬──────────┘
                               │
                         HTTP + Cookies
                               │
                    ┌──────────▼──────────┐
                    │ Backend (Django)    │
                    │ Port: 8000          │
                    │ /api/               │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ SQLite Database     │
                    │ db.sqlite3          │
                    └─────────────────────┘
```

---

## 🔗 Endpoints Principales

### Autenticación
| Método | Endpoint | Requiere Auth |
|--------|----------|---------------|
| POST | `/api/auth/login/` | ❌ No |
| POST | `/api/auth/register/` | ❌ No |
| GET | `/api/auth/me/` | ✅ Sí |
| POST | `/api/auth/logout/` | ✅ Sí |

### Recursos
| Recurso | Listar | Crear | Actualizar | Eliminar |
|---------|--------|-------|-----------|----------|
| Usuarios | ✅ | ✅* | ✅* | ✅* |
| Máquinas | ✅ | ✅* | ✅* | ✅* |
| Solicitudes | ✅ | ✅* | ✅* | ✅* |
| Informes | ✅ | ✅* | ✅* | ✅* |

*Requiere autenticación

---

## 💡 Ejemplos Rápidos

### Login desde React
```javascript
import { useAuth } from './context/AuthContext';

function LoginPage() {
  const { login } = useAuth();

  const handleLogin = async () => {
    try {
      await login('jperez', 'ingeniero123');
      // Redirigir a dashboard
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return <button onClick={handleLogin}>Login</button>;
}
```

### Crear Solicitud
```javascript
import { createSolicitud } from './api/solicitudes';

async function handleCreateSolicitud() {
  try {
    const response = await createSolicitud({
      codigo_maquinaria: 1,
      id_usuario: 2,
      descripcion: 'Prueba de vibración',
      codigo_estado: 1,
    });
    console.log('Solicitud creada:', response.data);
    // ⚠️ Se envía email automáticamente a ingenieros
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Descargar PDF
```javascript
import { descargarPdfInforme } from './api/informes';

async function handleDownloadPdf(informeId) {
  try {
    const response = await descargarPdfInforme(informeId);
    
    // Crear descarga
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `informe_${informeId}.pdf`);
    document.body.appendChild(link);
    link.click();
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## ⚙️ Variables de Entorno

### Backend (.env)
```env
SECRET_KEY=django-insecure-dev-key-mantentask-2025-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

### Frontend (.env)
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

---

## 🐛 Troubleshooting

### "CSRF token missing" en login
✅ **Solucionado** - Middleware personalizado desactiva CSRF para `/api/`

### "Connection refused" al conectar desde React
- Verificar que Django está en `http://127.0.0.1:8000`
- Verificar que React está en `http://localhost:3000`
- Cambiar `API_BASE_URL` en `axiosConfig.js`

### Las cookies no se envían
- Verificar que `withCredentials: true` en axios
- Verificar que `CORS_ALLOW_ALL_ORIGINS = True` en Django

### Correos no llegan
- Verificar `.env` con credenciales correctas
- Verificar que el usuario tiene email válido
- Revisar carpeta de SPAM

---

## 📖 Documentación Completa

**Para referencia detallada:**
1. [API_COMPLETE_DOCS.md](./API_COMPLETE_DOCS.md) - Todos los endpoints
2. [FRONTEND_REACT_SETUP.md](./FRONTEND_REACT_SETUP.md) - Integración completa
3. [EXAMPLE_REACT_PROJECT.md](./EXAMPLE_REACT_PROJECT.md) - Código listo

---

## ✅ Checklist de Configuración

- [x] Backend configurado (Django)
- [x] Autenticación (Session Auth)
- [x] Base de datos (SQLite)
- [x] Correos (SMTP)
- [x] PDFs (ReportLab)
- [x] CORS habilitado
- [x] Documentación API
- [x] Documentación React
- [ ] Frontend React (tu tarea)
- [ ] Testing
- [ ] Deployment

---

## 🚢 Deployment (Futuro)

Para producción:
1. Cambiar `DEBUG = False`
2. Configurar `SECRET_KEY` segura
3. Configurar base de datos (PostgreSQL recomendado)
4. Configurar servidor web (Gunicorn + Nginx)
5. Habilitar HTTPS
6. Configurar variables de ambiente seguras

Ver [README.md](./README.md) para más detalles.

---

## 📞 Soporte

Si necesitas ayuda:

1. **Endpoint no funciona?**
   → Consulta [API_COMPLETE_DOCS.md](./API_COMPLETE_DOCS.md)

2. **No puedo conectar desde React?**
   → Consulta [FRONTEND_REACT_SETUP.md](./FRONTEND_REACT_SETUP.md)

3. **No tengo código de ejemplo?**
   → Copia de [EXAMPLE_REACT_PROJECT.md](./EXAMPLE_REACT_PROJECT.md)

4. **Error de correos?**
   → Consulta [EMAIL_CONFIG.md](./EMAIL_CONFIG.md)

---

**Sistema listo para desarrollar** ✨

**Última actualización:** Diciembre 10, 2025
