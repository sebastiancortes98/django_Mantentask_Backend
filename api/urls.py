from django.urls import path, include
from rest_framework import routers
from .views import (
    TipoUsuarioViewSet, NivelAccesoViewSet, SucursalViewSet,
    UsuarioViewSet, EstadoViewSet, MaquinaViewSet,
    SolicitudViewSet, InformeViewSet, TaskViewSet
)
from .auth import auth_login, auth_logout, auth_me, auth_register

# Router para endpoints REST
router = routers.DefaultRouter()
router.register(r'tipos-usuario', TipoUsuarioViewSet, basename='tipo-usuario')
router.register(r'niveles-acceso', NivelAccesoViewSet, basename='nivel-acceso')
router.register(r'sucursales', SucursalViewSet, basename='sucursal')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'estados', EstadoViewSet, basename='estado')
router.register(r'maquinas', MaquinaViewSet, basename='maquina')
router.register(r'solicitudes', SolicitudViewSet, basename='solicitud')
router.register(r'informes', InformeViewSet, basename='informe')

# Endpoint legacy
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # Autenticación
    path('auth/login/', auth_login, name='auth-login'),
    path('auth/logout/', auth_logout, name='auth-logout'),
    path('auth/me/', auth_me, name='auth-me'),
    path('auth/register/', auth_register, name='auth-register'),
    
    # REST endpoints
    path('', include(router.urls)),
]
