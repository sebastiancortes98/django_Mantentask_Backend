# Ejemplo de Proyecto React - MantenTask

Este archivo contiene código de ejemplo para un proyecto React completo integrando con la API de MantenTask.

## Estructura de carpetas

```
mantentask-frontend/
├── src/
│   ├── api/
│   │   ├── axiosConfig.js
│   │   ├── auth.js
│   │   ├── usuarios.js
│   │   ├── solicitudes.js
│   │   ├── informes.js
│   │   ├── maquinas.js
│   │   └── errorHandler.js
│   ├── context/
│   │   └── AuthContext.js
│   ├── components/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   ├── Dashboard.jsx
│   │   ├── ProtectedRoute.jsx
│   │   └── SolicitudesList.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   └── NotFoundPage.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Archivos de ejemplo

### 1. src/api/axiosConfig.js

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // IMPORTANTE: enviar cookies
});

// Interceptor para errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Sesión expirada');
      // Redirigir a login si es necesario
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2. src/api/auth.js

```javascript
import apiClient from './axiosConfig';

export const loginUser = async (username, password) => {
  const response = await apiClient.post('/auth/login/', {
    username,
    password,
  });
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await apiClient.post('/auth/register/', userData);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me/');
  return response.data.user;
};

export const logoutUser = async () => {
  await apiClient.post('/auth/logout/');
  localStorage.removeItem('user');
};
```

### 3. src/context/AuthContext.js

```javascript
import { createContext, useState, useContext, useEffect } from 'react';
import { loginUser, logoutUser, getCurrentUser } from '../api/auth';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch {
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const login = async (username, password) => {
    const response = await loginUser(username, password);
    setUser(response.user);
    setIsAuthenticated(true);
    return response;
  };

  const logout = async () => {
    await logoutUser();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe estar dentro de AuthProvider');
  }
  return context;
}
```

### 4. src/components/ProtectedRoute.jsx

```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <p>Cargando...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
}
```

### 5. src/components/LoginForm.jsx

```javascript
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export function LoginForm() {
  const [username, setUsername] = useState('jperez');
  const [password, setPassword] = useState('ingeniero123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.error || 'Error en login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2>Login</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <div>
        <label>Usuario:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div>
        <label>Contraseña:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px' }}>
        {loading ? 'Cargando...' : 'Login'}
      </button>

      <p>
        ¿No tienes cuenta? <a href="/register">Registrate aquí</a>
      </p>
    </form>
  );
}
```

### 6. src/components/Dashboard.jsx

```javascript
import { useAuth } from '../context/AuthContext';
import { useState, useEffect } from 'react';
import { getSolicitudes } from '../api/solicitudes';

export function Dashboard() {
  const { user, logout, isAuthenticated } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchSolicitudes();
    }
  }, [isAuthenticated]);

  const fetchSolicitudes = async () => {
    setLoading(true);
    try {
      const response = await getSolicitudes();
      setSolicitudes(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar solicitudes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated || !user) {
    return <p>Debes iniciar sesión</p>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>
          <h1>Bienvenido, {user.nombre_completo}</h1>
          <p>Nivel de acceso: {user.codigo_nivel_acceso}</p>
          <p>Correo: {user.correo_electronico}</p>
        </div>
        <button onClick={logout} style={{ height: '40px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      <h2>Solicitudes recientes</h2>
      {loading ? (
        <p>Cargando solicitudes...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f0f0f0' }}>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>ID</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Máquina</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Descripción</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Estado</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>Usuario</th>
            </tr>
          </thead>
          <tbody>
            {solicitudes.map((solicitud) => (
              <tr key={solicitud.codigo_solicitud}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {solicitud.codigo_solicitud}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {solicitud.codigo_maquinaria?.modelo || 'N/A'}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {solicitud.descripcion}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {solicitud.codigo_estado?.nombre_estado || 'N/A'}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {solicitud.id_usuario?.nombre_completo || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

### 7. src/App.jsx

```javascript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginForm } from './components/LoginForm';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          <Route path="/" element={<Navigate to="/dashboard" />} />
          
          <Route path="*" element={<h1>404 - Página no encontrada</h1>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
```

### 8. package.json

```json
{
  "name": "mantentask-frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

### 9. vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## Pasos para comenzar

### 1. Crear proyecto
```bash
npm create vite@latest mantentask-frontend -- --template react
cd mantentask-frontend
npm install
```

### 2. Instalar dependencias
```bash
npm install axios react-router-dom
```

### 3. Copiar archivos
Copiar todos los archivos de ejemplo en sus respectivas carpetas

### 4. Iniciar servidor
```bash
npm run dev
```

Acceder a `http://localhost:3000`

### 5. Probar login
Usuario: `jperez`
Contraseña: `ingeniero123`

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| jperez | ingeniero123 | Ingeniero |
| mlopez | ingeniero123 | Ingeniero |
| crodriguez | encargado123 | Encargado |
| agarcia | encargado123 | Encargado |
| admin | admin123 | Administrador |

## Variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Luego usarla en `axiosConfig.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL;
```

## Siguientes pasos

1. Agregar formularios para crear solicitudes
2. Agregar gestión de máquinas
3. Agregar formularios para crear informes
4. Implementar descarga de PDFs
5. Agregar notificaciones
6. Mejorar diseño con CSS/Tailwind
7. Agregar validaciones de formularios
8. Implementar paginación
9. Agregar filtros avanzados
10. Deployar a producción
