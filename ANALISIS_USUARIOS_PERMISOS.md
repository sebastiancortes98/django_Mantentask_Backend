# Análisis de Usuarios y Niveles de Acceso

## Estado Actual del Sistema

### Códigos Definidos

#### Tipos de Usuario
- **1** = Ingeniero
- **2** = Encargado

#### Niveles de Acceso
- **1** = Básico
- **2** = Intermedio
- **3** = Avanzado
- **4** = Administrador

---

## Problemas Potenciales Identificados

### 1. ⚠️ Posible Inconsistencia: Ingenieros con Nivel Admin

**Problema:** El sistema permite que un ingeniero (`codigo_tipo_usuario=1`) tenga nivel de administrador (`codigo_nivel_acceso=4`).

**Riesgo:** 
- Los permisos en el código verifican **nivel de acceso** para acciones administrativas
- Un ingeniero con nivel 4 tendría permisos de admin aunque su rol sea ingeniero
- Esto puede causar confusión en los dashboards del frontend

**Ejemplo de código afectado:**
```python
# En cambiar_estado (views.py línea 325)
es_admin = user.codigo_nivel_acceso == 4  # ✅ Verifica nivel
es_encargado = user.codigo_tipo_usuario == 2  # ✅ Verifica tipo
```

**Recomendación:**
- Separar claramente roles (tipo_usuario) de permisos (nivel_acceso)
- Sugerencia de matriz:

| Tipo Usuario | Nivel Recomendado | Permisos |
|--------------|-------------------|----------|
| Ingeniero (1) | Básico (1) o Intermedio (2) | Ver/modificar solicitudes asignadas |
| Encargado (2) | Intermedio (2) o Avanzado (3) | Gestionar solicitudes, asignar ingenieros |
| Admin | Avanzado (3) o Administrador (4) | Control total |

---

### 2. ⚠️ Falta de Validación en Creación de Usuarios

**Problema:** El serializer de usuarios no valida la combinación tipo_usuario + nivel_acceso.

**Ubicación:** `api/serializers.py` - `UsuarioSerializer.create()`

**Riesgo:**
- Se pueden crear usuarios con combinaciones inválidas
- Ej: Encargado con nivel Básico (debería tener al menos Intermedio)

**Código actual:**
```python
def create(self, validated_data):
    # ...
    validated_data.setdefault('codigo_tipo_usuario', 1)  # Ingeniero
    validated_data.setdefault('codigo_nivel_acceso', 1)  # Básico
    # No hay validación de la combinación
```

**Solución sugerida:**
Agregar validación en el método `validate()`:
```python
def validate(self, attrs):
    tipo_usuario = attrs.get('codigo_tipo_usuario')
    nivel_acceso = attrs.get('codigo_nivel_acceso')
    
    # Validar combinaciones
    if tipo_usuario == 1 and nivel_acceso == 4:
        raise serializers.ValidationError(
            "Los ingenieros no deberían tener nivel de administrador"
        )
    
    if tipo_usuario == 2 and nivel_acceso == 1:
        raise serializers.ValidationError(
            "Los encargados deben tener nivel intermedio o superior"
        )
    
    return attrs
```

---

### 3. ⚠️ Permisos Mixtos: Tipo vs Nivel

**Problema:** El código mezcla verificaciones de `tipo_usuario` y `nivel_acceso` sin una lógica clara.

**Ejemplo en `cambiar_estado`:**
```python
es_admin = user.codigo_nivel_acceso == 4
es_encargado = user.codigo_tipo_usuario == 2
es_ingeniero = user.codigo_tipo_usuario == 1

if es_admin or es_encargado:
    pass  # Pueden cambiar cualquier solicitud
```

**Riesgo:**
- Un ingeniero con nivel 4 tendría permisos de admin
- Un encargado siempre puede cambiar estados sin importar su nivel

**Solución sugerida:**
Definir claramente la jerarquía:
```python
# Opción 1: Solo nivel de acceso importa (más simple)
es_admin = user.codigo_nivel_acceso >= 4
puede_gestionar = user.codigo_nivel_acceso >= 3

# Opción 2: Combinar tipo y nivel
es_admin = user.codigo_nivel_acceso == 4
es_encargado_avanzado = user.codigo_tipo_usuario == 2 and user.codigo_nivel_acceso >= 2
puede_gestionar = es_admin or es_encargado_avanzado
```

---

### 4. ✅ Permisos Correctos en permissions.py

Los permisos personalizados están bien implementados:

```python
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.codigo_nivel_acceso == 4

class IsEngineer(BasePermission):
    def has_permission(self, request, view):
        return request.user.codigo_tipo_usuario == 1
```

**Buenas prácticas:**
- Verifican autenticación
- Usan campos correctos
- Mensajes de error claros

---

### 5. ⚠️ Endpoints sin Verificación de Tipo Usuario

**Ubicación:** `api/views.py` - Varios endpoints

**Problema:** Algunos endpoints solo verifican `nivel_acceso` y no `tipo_usuario`.

**Ejemplo:** `asignar_ingeniero` (línea 395)
```python
es_admin = user.codigo_nivel_acceso == 4
es_encargado = user.codigo_tipo_usuario == 2

if not (es_admin or es_encargado):
    return Response({'error': '...'}, status=403)
```

**Análisis:**
- ✅ Correcto: Verifica ambos
- ⚠️ Pero un ingeniero con nivel 4 podría asignar ingenieros

**Sugerencia:**
```python
# Opción más estricta
puede_asignar = (
    user.codigo_nivel_acceso == 4 or  # Admin siempre puede
    (user.codigo_tipo_usuario == 2 and user.codigo_nivel_acceso >= 2)  # Encargados nivel 2+
)
```

---

## Recomendaciones de Implementación

### Opción A: Jerarquía Simple (RECOMENDADO)

**Concepto:** El `nivel_acceso` define los permisos, el `tipo_usuario` es solo informativo.

**Matriz de permisos:**
```
Nivel 1 (Básico):
  - Ver solicitudes asignadas
  - Ver informes propios
  - Actualizar perfil

Nivel 2 (Intermedio):
  - Lo de nivel 1 +
  - Cambiar estado de solicitudes asignadas
  - Crear informes

Nivel 3 (Avanzado):
  - Lo de nivel 2 +
  - Ver todas las solicitudes
  - Asignar ingenieros
  - Gestionar cualquier solicitud

Nivel 4 (Administrador):
  - Todo lo anterior +
  - Crear/editar usuarios
  - Cambiar niveles de acceso
  - Acceso total al sistema
```

**Ventaja:** Más flexible y fácil de mantener

---

### Opción B: Roles + Niveles Combinados

**Concepto:** El `tipo_usuario` define el rol, el `nivel_acceso` afina los permisos dentro del rol.

**Matriz de permisos:**
```
Ingeniero (tipo=1):
  Básico (1): Solo solicitudes asignadas
  Intermedio (2): + Crear informes, cambiar estados
  Avanzado (3): + Ver todas las solicitudes de su sucursal

Encargado (tipo=2):
  Intermedio (2): Gestionar solicitudes, asignar ingenieros
  Avanzado (3): + Ver reportes, estadísticas avanzadas
  Administrador (4): Control total

Admin del sistema:
  Administrador (4): Gestión completa, usuarios, configuración
```

**Ventaja:** Más granular pero más complejo

---

## Script de Verificación

He creado `verificar_usuarios.py` que detecta:

1. ✅ Usuarios con `tipo_usuario` fuera de rango (1, 2)
2. ✅ Usuarios con `nivel_acceso` fuera de rango (1-4)
3. ⚠️ Ingenieros con nivel de administrador
4. ⚠️ Encargados con nivel básico
5. ✅ Usuarios sin correo electrónico
6. ✅ Superusers sin nivel administrador

**Ejecutar en producción:**
```bash
python manage.py shell < verificar_usuarios.py
```

O directamente:
```bash
python manage.py shell -c "exec(open('verificar_usuarios.py').read())"
```

---

## Plan de Acción Sugerido

### Fase 1: Diagnóstico (AHORA)
1. ✅ Ejecutar `verificar_usuarios.py` en producción
2. ✅ Identificar usuarios con combinaciones problemáticas
3. ✅ Documentar estado actual

### Fase 2: Corrección de Datos
1. Corregir usuarios con combinaciones inválidas
2. Estandarizar niveles según rol:
   - Ingenieros → nivel 1 o 2
   - Encargados → nivel 2 o 3
   - Admins → nivel 4

### Fase 3: Validaciones en Código
1. Agregar validación en `UsuarioSerializer`
2. Agregar restricciones en endpoints críticos
3. Documentar matriz de permisos

### Fase 4: Testing
1. Probar creación de usuarios con combinaciones inválidas
2. Verificar permisos en endpoints críticos
3. Validar flujos completos por tipo de usuario

---

## Código para Corregir Usuarios

Si se identifican problemas, usar este script:

```python
from api.models import Usuario

# Corregir ingenieros con nivel admin
ingenieros_admin = Usuario.objects.filter(codigo_tipo_usuario=1, codigo_nivel_acceso=4)
for ingeniero in ingenieros_admin:
    print(f"Corrigiendo {ingeniero.username}: nivel 4 → 2")
    ingeniero.codigo_nivel_acceso = 2
    ingeniero.save()

# Corregir encargados con nivel básico
encargados_basico = Usuario.objects.filter(codigo_tipo_usuario=2, codigo_nivel_acceso=1)
for encargado in encargados_basico:
    print(f"Corrigiendo {encargado.username}: nivel 1 → 2")
    encargado.codigo_nivel_acceso = 2
    encargado.save()

print("Correcciones completadas")
```

---

## Resumen de Hallazgos

### ✅ Aspectos Correctos
- Permisos personalizados bien implementados
- Campos del modelo correctamente definidos
- Endpoints críticos tienen validaciones de permisos
- Logging de cambios implementado

### ⚠️ Áreas de Mejora
- Validar combinaciones tipo_usuario + nivel_acceso al crear
- Documentar claramente la matriz de permisos
- Considerar si nivel_acceso debe ser independiente del tipo
- Agregar restricciones más estrictas en ciertos endpoints

### 🔴 Riesgos Potenciales
- Ingenieros con nivel 4 tendrían permisos de admin
- Encargados con nivel 1 podrían tener permisos insuficientes
- Falta de validación puede crear combinaciones inválidas

---

## Próximos Pasos

1. **INMEDIATO:** Ejecutar `verificar_usuarios.py` en producción para ver estado real
2. **CORTO PLAZO:** Corregir usuarios con combinaciones problemáticas
3. **MEDIANO PLAZO:** Implementar validaciones en serializers
4. **LARGO PLAZO:** Refactorizar matriz de permisos según opción elegida (A o B)

---

## Contacto

Para aplicar correcciones o ajustar la lógica de permisos, referirse a:
- Modelo: `api/models.py` → Clase `Usuario`
- Permisos: `api/permissions.py`
- Validaciones: `api/serializers.py` → `UsuarioSerializer`
- Lógica de negocio: `api/views.py` → Endpoints de solicitudes
