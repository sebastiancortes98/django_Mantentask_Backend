"""
Script de verificacion de usuarios y niveles de acceso

Ejecutar con: python manage.py shell < verificar_usuarios_simple.py
"""

from api.models import Usuario
from django.db.models import Count, Q

print("=" * 80)
print("VERIFICACION DE USUARIOS Y NIVELES DE ACCESO")
print("=" * 80)

# Resumen general
total_usuarios = Usuario.objects.count()
usuarios_activos = Usuario.objects.filter(is_active=True).count()
usuarios_inactivos = Usuario.objects.filter(is_active=False).count()

print(f"\nRESUMEN GENERAL:")
print(f"   Total de usuarios: {total_usuarios}")
print(f"   Usuarios activos: {usuarios_activos}")
print(f"   Usuarios inactivos: {usuarios_inactivos}")

# Distribucion por tipo de usuario
print(f"\nDISTRIBUCION POR TIPO DE USUARIO:")
tipos = Usuario.objects.values('codigo_tipo_usuario').annotate(total=Count('id_usuario'))
for tipo in tipos:
    tipo_nombre = dict(Usuario.TIPO_USUARIO_CHOICES).get(tipo['codigo_tipo_usuario'], 'Desconocido')
    print(f"   {tipo_nombre} (codigo {tipo['codigo_tipo_usuario']}): {tipo['total']} usuarios")

# Distribucion por nivel de acceso
print(f"\nDISTRIBUCION POR NIVEL DE ACCESO:")
niveles = Usuario.objects.values('codigo_nivel_acceso').annotate(total=Count('id_usuario'))
for nivel in niveles:
    nivel_nombre = dict(Usuario.NIVEL_ACCESO_CHOICES).get(nivel['codigo_nivel_acceso'], 'Desconocido')
    print(f"   {nivel_nombre} (codigo {nivel['codigo_nivel_acceso']}): {nivel['total']} usuarios")

# Identificar problemas potenciales
print(f"\nVERIFICACION DE PROBLEMAS:")

# 1. Usuarios con tipo_usuario no valido
usuarios_tipo_invalido = Usuario.objects.exclude(
    codigo_tipo_usuario__in=[choice[0] for choice in Usuario.TIPO_USUARIO_CHOICES]
)
if usuarios_tipo_invalido.exists():
    print(f"   ERROR: {usuarios_tipo_invalido.count()} usuarios con tipo_usuario invalido:")
    for u in usuarios_tipo_invalido:
        print(f"      - {u.username} (tipo: {u.codigo_tipo_usuario})")
else:
    print(f"   OK: Todos los usuarios tienen tipo_usuario valido (1=Ingeniero, 2=Encargado)")

# 2. Usuarios con nivel_acceso no valido
usuarios_nivel_invalido = Usuario.objects.exclude(
    codigo_nivel_acceso__in=[choice[0] for choice in Usuario.NIVEL_ACCESO_CHOICES]
)
if usuarios_nivel_invalido.exists():
    print(f"   ERROR: {usuarios_nivel_invalido.count()} usuarios con nivel_acceso invalido:")
    for u in usuarios_nivel_invalido:
        print(f"      - {u.username} (nivel: {u.codigo_nivel_acceso})")
else:
    print(f"   OK: Todos los usuarios tienen nivel_acceso valido (1-4)")

# 3. Ingenieros con nivel de administrador (problema potencial)
ingenieros_admin = Usuario.objects.filter(
    codigo_tipo_usuario=1,  # Ingeniero
    codigo_nivel_acceso=4   # Administrador
)
if ingenieros_admin.exists():
    print(f"   ADVERTENCIA: {ingenieros_admin.count()} ingenieros con nivel de administrador:")
    for u in ingenieros_admin:
        print(f"      - {u.username} - {u.get_full_name()}")
else:
    print(f"   OK: No hay ingenieros con nivel de administrador")

# 4. Ingenieros con nivel 3 (Avanzado)
ingenieros_avanzado = Usuario.objects.filter(
    codigo_tipo_usuario=1,
    codigo_nivel_acceso=3
)
if ingenieros_avanzado.exists():
    print(f"   ADVERTENCIA: {ingenieros_avanzado.count()} ingenieros con nivel avanzado:")
    for u in ingenieros_avanzado:
        print(f"      - {u.username} - {u.get_full_name()}")
else:
    print(f"   OK: No hay ingenieros con nivel avanzado")

# 5. Encargados sin nivel intermedio o avanzado
encargados_basico = Usuario.objects.filter(
    codigo_tipo_usuario=2,  # Encargado
    codigo_nivel_acceso=1   # Basico
)
if encargados_basico.exists():
    print(f"   ADVERTENCIA: {encargados_basico.count()} encargados con nivel basico:")
    for u in encargados_basico:
        print(f"      - {u.username} - {u.get_full_name()}")
else:
    print(f"   OK: Todos los encargados tienen nivel intermedio o superior")

# 6. Usuarios activos sin correo electronico
usuarios_sin_email = Usuario.objects.filter(is_active=True).filter(
    Q(correo_electronico='') | Q(correo_electronico__isnull=True)
)
if usuarios_sin_email.exists():
    print(f"   ADVERTENCIA: {usuarios_sin_email.count()} usuarios activos sin correo electronico:")
    for u in usuarios_sin_email:
        print(f"      - {u.username}")
else:
    print(f"   OK: Todos los usuarios activos tienen correo electronico")

# 7. Usuarios superuser que no son administradores
superusers_no_admin = Usuario.objects.filter(is_superuser=True).exclude(codigo_nivel_acceso=4)
if superusers_no_admin.exists():
    print(f"   ADVERTENCIA: {superusers_no_admin.count()} superusuarios sin nivel de administrador:")
    for u in superusers_no_admin:
        print(f"      - {u.username} (nivel: {u.get_codigo_nivel_acceso_display()})")
else:
    print(f"   OK: Todos los superusuarios tienen nivel de administrador")

# Listado detallado de todos los usuarios activos
print(f"\nLISTADO DETALLADO DE USUARIOS ACTIVOS:")
print(f"{'Username':<20} {'Nombre Completo':<30} {'Tipo':<12} {'Nivel':<15} {'Superuser':<10}")
print("-" * 95)

usuarios = Usuario.objects.filter(is_active=True).order_by('codigo_tipo_usuario', 'codigo_nivel_acceso')
for u in usuarios:
    username = u.username[:19]
    nombre = u.get_full_name()[:29]
    tipo = u.get_codigo_tipo_usuario_display()[:11]
    nivel = u.get_codigo_nivel_acceso_display()[:14]
    superuser = "Si" if u.is_superuser else "No"
    print(f"{username:<20} {nombre:<30} {tipo:<12} {nivel:<15} {superuser:<10}")

# Recomendaciones
print(f"\nRECOMENDACIONES:")
print(f"   1. Ingenieros deben tener nivel Basico (1) o Intermedio (2)")
print(f"   2. Encargados deben tener nivel Intermedio (2) o Avanzado (3)")
print(f"   3. Administradores del sistema deben tener nivel Administrador (4)")
print(f"   4. Solo debe haber tipo_usuario = 1 (Ingeniero) o 2 (Encargado)")
print(f"   5. Solo debe haber nivel_acceso entre 1 y 4")

print(f"\n{'=' * 80}")
print("VERIFICACION COMPLETADA")
print("=" * 80)
