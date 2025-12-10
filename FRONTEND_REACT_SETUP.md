# Guía de Integración: React + Axios con MantenTask API

## Tabla de Contenidos
1. [Instalación](#instalación)
2. [Configuración de Axios](#configuración-de-axios)
3. [Autenticación](#autenticación)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Manejo de Errores](#manejo-de-errores)
6. [Context API para Autenticación](#context-api-para-autenticación)

---

## Instalación

### 1. Instalar Axios
```bash
npm install axios
```

### 2. Versiones recomendadas
```json
{
  "react": "^18.0.0",
  "axios": "^1.6.0"
}
```

---

## Configuración de Axios

### Archivo: `src/api/axiosConfig.js`

```javascript
import axios from 'axios';

// URL base de la API
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Importante: enviar cookies en requests
  withCredentials: true,
});

// Interceptor para manejar errores globales
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Usuario no autenticado - redirigir a login
      console.warn('Sesión expirada');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Uso básico:
```javascript
import apiClient from './api/axiosConfig';

// GET
apiClient.get('/usuarios/').then(res => console.log(res.data));

// POST
apiClient.post('/auth/login/', {
  username: 'jperez',
  password: 'ingeniero123'
}).then(res => console.log(res.data));
```

---

## Autenticación

### 1. Login
```javascript
// src/api/auth.js
import apiClient from './axiosConfig';

export const loginUser = async (username, password) => {
  try {
    const response = await apiClient.post('/auth/login/', {
      username,
      password,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};
```

**Uso en componente:**
```javascript
import { loginUser } from './api/auth';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const userData = await loginUser(username, password);
      console.log('Login exitoso:', userData);
      // Guardar usuario en estado/localStorage
      localStorage.setItem('user', JSON.stringify(userData.user));
      // Redirigir a dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.error || 'Error en login');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
}

export default LoginForm;
```

---

### 2. Registro
```javascript
// src/api/auth.js
export const registerUser = async (userData) => {
  try {
    const response = await apiClient.post('/auth/register/', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};
```

**Uso:**
```javascript
const handleRegister = async (formData) => {
  try {
    const result = await registerUser({
      username: formData.username,
      password: formData.password,
      first_name: formData.first_name,
      apellido_paterno: formData.apellido_paterno,
      apellido_materno: formData.apellido_materno,
      correo_electronico: formData.correo_electronico,
      codigo_tipo_usuario: 1,
      codigo_nivel_acceso: 2,
      codigo_sucursal: 1,
    });
    console.log('Usuario registrado:', result);
  } catch (error) {
    console.error('Error en registro:', error);
  }
};
```

---

### 3. Obtener usuario actual
```javascript
// src/api/auth.js
export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/auth/me/');
    return response.data.user;
  } catch (error) {
    throw error.response?.data || error;
  }
};
```

---

### 4. Logout
```javascript
// src/api/auth.js
export const logoutUser = async () => {
  try {
    await apiClient.post('/auth/logout/');
    localStorage.removeItem('user');
    window.location.href = '/login';
  } catch (error) {
    console.error('Error en logout:', error);
  }
};
```

---

## Ejemplos de Uso

### Usuarios

```javascript
// src/api/usuarios.js
import apiClient from './axiosConfig';

// Listar usuarios
export const getUsuarios = async (filters = {}) => {
  try {
    const response = await apiClient.get('/usuarios/', { params: filters });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Obtener usuario específico
export const getUsuario = async (id) => {
  try {
    const response = await apiClient.get(`/usuarios/${id}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Crear usuario
export const createUsuario = async (userData) => {
  try {
    const response = await apiClient.post('/usuarios/', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.errors || error;
  }
};

// Actualizar usuario
export const updateUsuario = async (id, userData) => {
  try {
    const response = await apiClient.patch(`/usuarios/${id}/`, userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Eliminar usuario
export const deleteUsuario = async (id) => {
  try {
    await apiClient.delete(`/usuarios/${id}/`);
    return true;
  } catch (error) {
    throw error;
  }
};

// Listar ingenieros
export const getIngenieros = async () => {
  try {
    const response = await apiClient.get('/usuarios/ingenieros/');
    return response.data;
  } catch (error) {
    throw error;
  }
};
```

**Uso en componente:**
```javascript
import { getUsuarios, createUsuario } from './api/usuarios';

function UsuariosList() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUsuarios = async () => {
      setLoading(true);
      try {
        const data = await getUsuarios({ page: 1 });
        setUsuarios(data.results || data);
      } catch (error) {
        console.error('Error al cargar usuarios:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchUsuarios();
  }, []);

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h2>Usuarios</h2>
      <ul>
        {usuarios.map((usuario) => (
          <li key={usuario.id_usuario}>
            {usuario.nombre_completo} ({usuario.username})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

### Solicitudes

```javascript
// src/api/solicitudes.js
import apiClient from './axiosConfig';

export const getSolicitudes = async (filters = {}) => {
  return apiClient.get('/solicitudes/', { params: filters });
};

export const getSolicitud = async (id) => {
  return apiClient.get(`/solicitudes/${id}/`);
};

export const createSolicitud = async (solicitudData) => {
  return apiClient.post('/solicitudes/', solicitudData);
};

export const updateSolicitud = async (id, solicitudData) => {
  return apiClient.patch(`/solicitudes/${id}/`, solicitudData);
};

export const cambiarEstadoSolicitud = async (id, nuevoEstado) => {
  return apiClient.post(`/solicitudes/${id}/cambiar_estado/`, {
    codigo_estado: nuevoEstado,
  });
};

export const getSolicitudesPendientes = async () => {
  return apiClient.get('/solicitudes/pendientes/');
};

export const getSolicitudesCompletadas = async () => {
  return apiClient.get('/solicitudes/completadas/');
};
```

**Uso completo:**
```javascript
import { createSolicitud, cambiarEstadoSolicitud } from './api/solicitudes';

function CrearSolicitud() {
  const [formData, setFormData] = useState({
    codigo_maquinaria: '',
    id_usuario: '',
    descripcion: '',
    codigo_estado: 1,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await createSolicitud(formData);
      alert('Solicitud creada con éxito');
      console.log('Respuesta:', result.data);
      // ⚠️ Se envía email automáticamente a ingenieros
    } catch (error) {
      alert('Error al crear solicitud: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        placeholder="ID Máquina"
        value={formData.codigo_maquinaria}
        onChange={(e) =>
          setFormData({ ...formData, codigo_maquinaria: e.target.value })
        }
        required
      />
      <textarea
        placeholder="Descripción del problema"
        value={formData.descripcion}
        onChange={(e) =>
          setFormData({ ...formData, descripcion: e.target.value })
        }
        required
      />
      <button type="submit">Crear Solicitud</button>
    </form>
  );
}
```

---

### Informes

```javascript
// src/api/informes.js
import apiClient from './axiosConfig';

export const getInformes = async (filters = {}) => {
  return apiClient.get('/informes/', { params: filters });
};

export const getInforme = async (id) => {
  return apiClient.get(`/informes/${id}/`);
};

export const createInforme = async (informeData) => {
  return apiClient.post('/informes/', informeData);
};

export const descargarPdfInforme = async (id) => {
  // Respuesta es un PDF
  return apiClient.get(`/informes/${id}/descargar_pdf/`, {
    responseType: 'blob',
  });
};

export const enviarInformePorCorreo = async (id, email) => {
  return apiClient.post(`/informes/${id}/enviar_por_correo/`, {
    email,
  });
};

export const regenerarPdfInforme = async (id) => {
  return apiClient.post(`/informes/${id}/regenerar_pdf/`);
};
```

**Uso para descargar PDF:**
```javascript
const handleDescargarPdf = async (id) => {
  try {
    const response = await descargarPdfInforme(id);
    
    // Crear URL para descargar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `informe_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
  } catch (error) {
    console.error('Error al descargar PDF:', error);
  }
};
```

---

### Máquinas

```javascript
// src/api/maquinas.js
import apiClient from './axiosConfig';

export const getMaquinas = async (filters = {}) => {
  return apiClient.get('/maquinas/', { params: filters });
};

export const getMaquina = async (id) => {
  return apiClient.get(`/maquinas/${id}/`);
};

export const createMaquina = async (maquinaData) => {
  return apiClient.post('/maquinas/', maquinaData);
};

export const updateMaquina = async (id, maquinaData) => {
  return apiClient.patch(`/maquinas/${id}/`, maquinaData);
};

export const registrarMantenimiento = async (id) => {
  return apiClient.post(`/maquinas/${id}/registrar_mantenimiento/`);
};
```

---

### Catálogos

```javascript
// src/api/catalogos.js
import apiClient from './axiosConfig';

export const getTiposUsuario = async () => {
  return apiClient.get('/tipos-usuario/');
};

export const getNivelesAcceso = async () => {
  return apiClient.get('/niveles-acceso/');
};

export const getEstados = async () => {
  return apiClient.get('/estados/');
};

export const getSucursales = async () => {
  return apiClient.get('/sucursales/');
};
```

---

## Manejo de Errores

```javascript
// src/api/errorHandler.js
export const handleApiError = (error) => {
  const errorMessage = error.response?.data?.detail || 
                       error.response?.data?.error ||
                       error.message ||
                       'Error desconocido';
  
  return {
    status: error.response?.status,
    message: errorMessage,
    data: error.response?.data,
  };
};
```

**Uso:**
```javascript
import { handleApiError } from './api/errorHandler';

try {
  await createSolicitud(data);
} catch (error) {
  const { status, message } = handleApiError(error);
  
  if (status === 401) {
    console.log('Usuario no autenticado');
  } else if (status === 400) {
    console.log('Datos inválidos:', message);
  } else {
    console.log('Error:', message);
  }
}
```

---

## Context API para Autenticación

### Archivo: `src/context/AuthContext.js`

```javascript
import { createContext, useState, useContext, useEffect } from 'react';
import { loginUser, logoutUser, getCurrentUser } from '../api/auth';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Verificar si ya hay sesión activa
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await loginUser(username, password);
      setUser(response.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      setIsAuthenticated(false);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook para usar el contexto
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe estar dentro de AuthProvider');
  }
  return context;
}
```

**Uso en componentes:**
```javascript
import { useAuth } from './context/AuthContext';

function Dashboard() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <p>Debes iniciar sesión</p>;
  }

  return (
    <div>
      <h1>Bienvenido, {user.nombre_completo}</h1>
      <p>Nivel: {user.codigo_nivel_acceso}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default Dashboard;
```

---

## Estructura de Carpetas Recomendada

```
src/
├── api/
│   ├── axiosConfig.js       # Configuración de axios
│   ├── auth.js              # Funciones de autenticación
│   ├── usuarios.js          # API de usuarios
│   ├── solicitudes.js       # API de solicitudes
│   ├── informes.js          # API de informes
│   ├── maquinas.js          # API de máquinas
│   ├── catalogos.js         # Catálogos
│   └── errorHandler.js      # Manejo de errores
├── context/
│   └── AuthContext.js       # Context de autenticación
├── components/
│   ├── LoginForm.jsx
│   ├── Dashboard.jsx
│   ├── SolicitudesList.jsx
│   └── InformeForm.jsx
├── pages/
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   └── NotFound.jsx
├── App.jsx
└── main.jsx
```

---

## Checklist de Configuración

- [ ] Instalar axios: `npm install axios`
- [ ] Crear archivo `api/axiosConfig.js`
- [ ] Crear archivos de API (auth, usuarios, etc.)
- [ ] Crear `AuthContext.js` con AuthProvider
- [ ] Envolver App con `<AuthProvider>`
- [ ] Crear componentes de login
- [ ] Implementar protección de rutas
- [ ] Probar login/logout
- [ ] Probar crear solicitud
- [ ] Probar descargar PDF

---

## Notas Importantes

- ✅ **withCredentials: true** es OBLIGATORIO para que se envíen las cookies
- ✅ El servidor está en `http://127.0.0.1:8000` - cambiar en producción
- ✅ Los PDFs se descargan con `responseType: 'blob'`
- ✅ Los emails se envían automáticamente en ciertos eventos
- ✅ Usar `localStorage` para persistencia básica
- ✅ Para producción usar localStorage + refresh tokens (future implementation)
