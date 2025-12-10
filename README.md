Proyecto backend Django - Mantentask

Instrucciones rápidas (PowerShell, Windows):

1) Crear y activar entorno virtual:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

(Si PowerShell bloquea la ejecución: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)

2) Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3) Crear archivo `.env` a partir de `.env.example` y ajustar `SECRET_KEY` si quieres.

4) Aplicar migraciones y crear superusuario:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5) Ejecutar servidor:

```powershell
python manage.py runserver
```

## Sistema de Email

Para habilitar notificaciones automáticas por correo:

1. **Opción 1: Gmail (recomendado)**
   - Ve a https://myaccount.google.com/apppasswords
   - Genera una "Contraseña de aplicación"
   - En `.env`, configura:
     ```env
     EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     EMAIL_USE_TLS=True
     EMAIL_HOST_USER=tu-email@gmail.com
     EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
     DEFAULT_FROM_EMAIL=tu-email@gmail.com
     ```

2. **Opción 2: Outlook/Office365**
   ```env
   EMAIL_HOST=smtp.office365.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

3. **Prueba la configuración:**
   ```powershell
   python manage.py test_email --email tu-email@gmail.com
   ```

Ver `EMAIL_CONFIG.md` para más detalles.

## Datos de Prueba

Crea datos de prueba automáticamente:

```powershell
python manage.py create_test_data
```

Credenciales de prueba:
- Admin: `admin / admin123`
- Ingeniero: `jperez / ingeniero123`
- Encargado: `crodriguez / encargado123`

## API REST

La API completa está disponible en `/api/`. 

Endpoints principales:
- `GET /api/maquinas/` - Listar máquinas
- `GET /api/solicitudes/` - Listar solicitudes
- `GET /api/informes/` - Listar informes
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/solicitudes/` - Crear solicitud (envía notificación por correo)
- `POST /api/informes/` - Crear informe (genera PDF automático)

Ver `API_DOCUMENTATION.md` para documentación completa.

## Panel de Administración

Accede a `http://127.0.0.1:8000/admin/` con credenciales de superusuario.

## Ejecutar Pruebas

```powershell
python manage.py test
```

MySQL setup (opcional)

1. Si vas a usar MySQL, añade las variables en tu `.env`:

```
DB_NAME=mantentask_db
DB_USER=mantentask_user
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=3306
```

2. Crear base de datos y usuario (ejemplo PowerShell con cliente `mysql`):

```powershell
# Conéctate como root (se te pedirá contraseña)
mysql -u root -p -e "CREATE DATABASE mantentask_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; CREATE USER 'mantentask_user'@'localhost' IDENTIFIED BY 'change-me'; GRANT ALL PRIVILEGES ON mantentask_db.* TO 'mantentask_user'@'localhost'; FLUSH PRIVILEGES;"
```

Si prefieres usar una GUI (MySQL Workbench) o Docker, crea la base y el usuario equivalentes.

Docker (opción recomendada para desarrollo)

Puedes arrancar un contenedor MySQL local usando `docker-compose` incluido. Esto evita tener que instalar MySQL en tu máquina y te permite correr migraciones contra una base limpia.

1. Asegúrate de que Docker Desktop está instalado y funcionando.

2. Copia `.env.example` a `.env` y (opcionalmente) ajusta las variables `DB_*`. El `docker-compose.yml` usa estas variables para inicializar la base de datos.

3. Arranca el servicio MySQL:

```powershell
docker-compose up -d db
```

4. Espera unos segundos a que el contenedor esté listo, luego aplica migraciones y crea el superusuario:

```powershell
venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

5. Para detener y borrar los datos (si lo deseas):

```powershell
docker-compose down -v
```

3. Instalar dependencias e iniciar la app (PowerShell):

```powershell
# activar venv (si no lo has hecho)
python -m venv venv
venv\Scripts\Activate.ps1

# instalar dependencias (incluye PyMySQL)
pip install -r requirements.txt

# copia .env y edita
copy .env.example .env
# editar .env y añadir DB_* variables

# crear migraciones y aplicarlas
python manage.py makemigrations
python manage.py migrate

# crear superusuario
python manage.py createsuperuser

# ejecutar servidor
python manage.py runserver
```

Notas:
- La instalación de `PyMySQL` permite usar MySQL en entornos Windows sin compilar extensiones nativas. Para producción puedes usar `mysqlclient` si prefieres (requiere compilación o ruedas precompiladas).
- Si no defines `DB_NAME` en `.env`, el proyecto usará SQLite por defecto para un arranque rápido.
