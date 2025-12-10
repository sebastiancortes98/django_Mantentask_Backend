# Fix para AuthContext - Frontend

## Problema
El frontend retorna error 403 cuando intenta verificar la sesión al iniciar.

## Solución

En `src/context/AuthContext.jsx`, reemplaza la función `checkAuth` por esto:

### ❌ Código anterior (con problema):
```javascript
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
```

### ✅ Código correcto (sin problema):
```javascript
useEffect(() => {
  const checkAuth = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // 401 = No autenticado, 403 = Sesión expirada o no válida
      // Ambos casos significan que no hay sesión válida
      if (error.response?.status === 401 || error.response?.status === 403) {
        setIsAuthenticated(false);
      } else {
        console.error('Error al verificar autenticación:', error);
      }
    } finally {
      setLoading(false);
    }
  };
  checkAuth();
}, []);
```

## Explicación
- **403 Forbidden**: Usuario no autenticado (no tiene cookies válidas)
- **401 Unauthorized**: Usuario no tiene permisos

Ambos casos indican que el usuario **no está logueado**, así que simplemente ignoramos el error y continuamos.

## Resultado esperado
- ✅ El frontend cargará sin errores
- ✅ El usuario verá la página de login
- ✅ Al hacer login, se establecerán las cookies de sesión
- ✅ Los siguientes requests funcionarán correctamente
